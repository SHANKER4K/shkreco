import os
import pickle
from torchvision import transforms
import torch
import numpy as np
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1
from arcface_loss import ArcFaceLoss

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

mtcnn   = MTCNN(image_size=160, margin=20, keep_all=False, device=device)
resnet  = InceptionResnetV1(pretrained='vggface2').eval().to(device)

checkpoint = torch.load('checkpoints/arcface_best.pth', 
                       map_location=torch.device('cpu'))

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Recreate backbone and loss modules
backbone = InceptionResnetV1(pretrained='vggface2').to(device)
arc_loss = ArcFaceLoss(
    embedding_dim=512,
    num_classes=len(checkpoint['classes']),
    s=64.0,
    m=0.5,
).to(device)

# Load weights
backbone.load_state_dict(checkpoint['backbone'])
arc_loss.load_state_dict(checkpoint['arc_loss'])

# Switch to eval mode
backbone.eval()
arc_loss.eval()

# Prepare image
transform = transforms.Compose([
    transforms.Resize((160, 160)),
    transforms.ToTensor(),
    transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5]),
])

def build_database(workers_dir='dataset', out_file='worker_db.pkl'):
    database = {}
    if not os.path.exists(workers_dir):
        print(f"Error: Directory {workers_dir} not found")
        return {}

    workers  = [d for d in os.listdir(workers_dir)
                if os.path.isdir(os.path.join(workers_dir, d))]

    print(f"Workers found: {len(workers)}\n")

    for worker in workers:
        worker_path = os.path.join(workers_dir, worker)
        images      = [f for f in os.listdir(worker_path)
                       if f.endswith('.jpg')]

        embeddings = []
        failed     = 0

        for img_file in images:
            img_path = os.path.join(worker_path, img_file)
            try:
                img         = Image.open(img_path).convert('RGB')
                face_tensor = mtcnn(img)

                if face_tensor is not None:
                    face_tensor = face_tensor.unsqueeze(0).to(device)
                    with torch.no_grad():
                        emb = backbone(face_tensor)
                    embeddings.append(emb.cpu().numpy().flatten())
                else:
                    failed += 1
            except Exception as e:
                print(f"  خطأ في {img_file}: {e}")
                failed += 1

        if len(embeddings) == 0:
            print(f"Warning: No faces found for {worker} — skipping")
            continue

        # Use Median instead of Mean to filter out outliers (incorrectly detected faces)
        embeddings_stack = np.stack(embeddings)
        median_embedding = np.median(embeddings_stack, axis=0)
        
        # Unit normalization (L2)
        norm = np.linalg.norm(median_embedding)
        database[worker] = (median_embedding / norm).astype(np.float32)

        print(f"  {worker}: {len(embeddings)} success"
              f"{f', {failed} failed' if failed else ''}")

    # Save database
    with open(out_file, 'wb') as f:
        pickle.dump(database, f)

    print(f"\nDatabase saved: {out_file}")
    print(f"Registered workers: {list(database.keys())}")
    return database


if __name__ == '__main__':
    build_database(workers_dir='dataset', out_file='worker_db_local.pkl')