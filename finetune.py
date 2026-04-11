import os
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from facenet_pytorch import InceptionResnetV1
from PIL import Image
from arcface_loss import ArcFaceLoss


# ──────────────────────────────────────────
# Dataset
# ──────────────────────────────────────────

class FaceDataset(Dataset):
    """
    Dataset بسيط من مجلدات — كل مجلد = شخص واحد.
    dataset/
      Colin_Powell/  000.jpg  001.jpg ...
      George_W_Bush/ 000.jpg ...
    """

    def __init__(self, root_dir, transform=None):
        self.samples   = []   # [(image_path, class_idx), ...]
        self.classes   = []
        self.transform = transform

        for idx, person in enumerate(sorted(os.listdir(root_dir))):
            person_path = os.path.join(root_dir, person)
            if not os.path.isdir(person_path):
                continue
            self.classes.append(person)
            for img_file in os.listdir(person_path):
                if img_file.endswith('.jpg'):
                    self.samples.append(
                        (os.path.join(person_path, img_file), idx)
                    )

        print(f"Dataset: {len(self.classes)} كلاس, "
              f"{len(self.samples)} صورة")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        img = Image.open(path).convert('RGB')
        if self.transform:
            img = self.transform(img)
        return img, label


# ArcFace يستخدم 112×112 (وليس 160 مثل FaceNet)
transform = transforms.Compose([
    transforms.Resize((160, 160)),
    transforms.RandomHorizontalFlip(),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.ToTensor(),
    transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5]),
])


# ──────────────────────────────────────────
# Fine-tuning
# ──────────────────────────────────────────

def finetune(data_dir='dataset', epochs=20,
             save_dir='checkpoints', lr=0.0001):

    os.makedirs(save_dir, exist_ok=True)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"الجهاز: {device}\n")

    # Dataset و DataLoader
    dataset     = FaceDataset(data_dir, transform=transform)
    loader      = DataLoader(dataset, batch_size=16,
                             shuffle=True, num_workers=2)
    num_classes = len(dataset.classes)

    # ── النموذج ──
    # Backbone: أوزان VGGFace2 الجاهزة — تفهم الوجوه بشكل عام
    backbone = InceptionResnetV1(pretrained='vggface2').to(device)

    # تجميد كل الطبقات ما عدا الأخيرة
    # نحن نريد فقط تكييف الطبقات الأخيرة على بياناتنا
    for name, param in backbone.named_parameters():
        if 'block8' not in name and 'last_linear' not in name:
            param.requires_grad = False

    unfrozen = sum(p.numel() for p in backbone.parameters()
                   if p.requires_grad)
    total    = sum(p.numel() for p in backbone.parameters())
    print(f"معاملات مُدرَّبة: {unfrozen:,} / {total:,} "
          f"({unfrozen/total*100:.1f}%)\n")

    # Loss Head: ArcFace الذي طبّقناه من الورقة
    # هذا ما يجعل المشروع أكاديمياً — نستخدم تطبيقنا الخاص
    arc_loss = ArcFaceLoss(
        embedding_dim=512,
        num_classes=num_classes,
        s=64.0,    # scale — section 3.3
        m=0.5,     # angular margin — section 3.1
    ).to(device)

    # Optimizer — يُحسّن فقط المعاملات غير المجمّدة + ArcFace head
    optimizer = torch.optim.Adam([
        {'params': filter(lambda p: p.requires_grad,
                          backbone.parameters()), 'lr': lr},
        {'params': arc_loss.parameters(),          'lr': lr * 10},
    ])

    # LR Scheduler — يُقلّل LR بمقدار النصف كل 7 epochs
    scheduler = torch.optim.lr_scheduler.StepLR(
        optimizer, step_size=7, gamma=0.5
    )

    # Mixed Precision — يُسرّع التدريب على T4 بحوالي 2x
    scaler = torch.cuda.amp.GradScaler(
        enabled=(device.type == 'cuda')
    )

    # Load from checkpoint if it exists
    best_loss = float('inf')
    start_epoch = 0
    checkpoint_path = os.path.join(save_dir, 'arcface_best.pth')
    
    if os.path.exists(checkpoint_path):
        print(f"جاري تحميل checkpoint من: {checkpoint_path}")
        checkpoint = torch.load(checkpoint_path, map_location=device)
        backbone.load_state_dict(checkpoint['backbone'])
        arc_loss.load_state_dict(checkpoint['arc_loss'])
        best_loss = checkpoint['loss']
        start_epoch = checkpoint['epoch']
        print(f"تم استئناف التدريب من epoch {start_epoch} "
              f"(أفضل loss: {best_loss:.4f})\n")
    else:
        print("لا يوجد checkpoint — بدء تدريب جديد\n")

    print("بدء التدريب...\n" + "─"*45)

    for epoch in range(start_epoch, epochs):
        backbone.train()
        arc_loss.train()
        total_loss = 0

        for batch_idx, (images, labels) in enumerate(loader):
            images = images.to(device)
            labels = labels.to(device)

            with torch.cuda.amp.autocast(
                enabled=(device.type == 'cuda')
            ):
                # Forward: backbone → embedding → ArcFace loss
                embeddings = backbone(images)
                loss       = arc_loss(embeddings, labels)

            optimizer.zero_grad()
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()

            total_loss += loss.item()

        scheduler.step()
        
        avg_loss = total_loss / len(loader)
        lr_now   = scheduler.get_last_lr()[0]
        print(f"Epoch {epoch+1:02d}/{epochs} | "
              f"Loss: {avg_loss:.4f} | "
              f"LR: {lr_now:.6f}")

        # حفظ أفضل نموذج
        if avg_loss < best_loss:
            best_loss = avg_loss
            path = os.path.join(save_dir, 'arcface_best.pth')
            torch.save({
                'epoch':     epoch + 1,
                'backbone':  backbone.state_dict(),
                'arc_loss':  arc_loss.state_dict(),
                'loss':      best_loss,
                'classes':   dataset.classes,
            }, path)
            print(f"  → حُفظ أفضل نموذج (loss: {best_loss:.4f})")

    print("\n" + "─"*45)
    print(f"اكتمل التدريب. أفضل loss: {best_loss:.4f}")
    print(f"النموذج محفوظ في: {save_dir}/arcface_best.pth")
    return backbone, arc_loss, dataset.classes


if __name__ == '__main__':
    finetune(
        data_dir='data/train',
        epochs=60,
        save_dir='checkpoints',
    )