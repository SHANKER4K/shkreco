import os
import pickle
import torch
import numpy as np
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

mtcnn   = MTCNN(image_size=160, margin=20, keep_all=False, device=device)
resnet  = InceptionResnetV1(pretrained='vggface2').eval().to(device)

def build_database(workers_dir='dataset', out_file='worker_db.pkl'):
    database = {}
    workers  = [d for d in os.listdir(workers_dir)
                if os.path.isdir(os.path.join(workers_dir, d))]

    print(f"عدد العمال: {len(workers)}\n")

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
                        emb = resnet(face_tensor)
                    embeddings.append(emb.cpu().numpy().flatten())
                else:
                    failed += 1
            except Exception as e:
                print(f"  خطأ في {img_file}: {e}")
                failed += 1

        if len(embeddings) == 0:
            print(f"تحذير: لا توجد وجوه لـ {worker} — تجاهَل")
            continue

        # المتوسط أقوى من صورة واحدة
        mean_embedding      = np.mean(embeddings, axis=0)
        # L2 normalize
        norm                = np.linalg.norm(mean_embedding)
        database[worker]    = mean_embedding / norm

        print(f"  {worker}: {len(embeddings)} صورة ناجحة"
              f"{f', {failed} فاشلة' if failed else ''}")

    # حفظ قاعدة البيانات
    with open(out_file, 'wb') as f:
        pickle.dump(database, f)

    print(f"\nقاعدة البيانات محفوظة: {out_file}")
    print(f"العمال المسجلون: {list(database.keys())}")
    return database


if __name__ == '__main__':
    build_database(workers_dir='dataset', out_file='worker_db_local.pkl')