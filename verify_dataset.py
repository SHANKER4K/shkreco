import os
import pickle
import numpy as np
from PIL import Image
from facenet_pytorch import MTCNN
import torch

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
mtcnn  = MTCNN(keep_all=False, device=device)

def verify_dataset(workers_dir='dataset', db_file='worker_db.pkl'):
    print("=" * 45)
    print("فحص Dataset")
    print("=" * 45)

    # 1 — فحص المجلدات
    workers = [d for d in os.listdir(workers_dir)
               if os.path.isdir(os.path.join(workers_dir, d))]

    all_good = True
    for worker in workers:
        path   = os.path.join(workers_dir, worker)
        images = [f for f in os.listdir(path) if f.endswith('.jpg')]
        status = "✓" if len(images) >= 10 else "✗ أقل من 10 صور"
        print(f"  {worker}: {len(images)} صورة — {status}")
        if len(images) < 10:
            all_good = False

    # 2 — فحص قاعدة البيانات
    print()
    if os.path.exists(db_file):
        with open(db_file, 'rb') as f:
            db = pickle.load(f)
        print(f"قاعدة البيانات: {len(db)} عامل مسجّل")
        for name, emb in db.items():
            norm = np.linalg.norm(emb)
            print(f"  {name}: embedding shape={emb.shape},"
                  f" norm={norm:.4f} (يجب أن يكون ~1.0)")
    else:
        print("قاعدة البيانات غير موجودة — شغّل build_database.py أولاً")
        all_good = False

    print()
    if all_good:
        print("الحالة: كل شيء جاهز — انتقل للمرحلة الثالثة")
    else:
        print("الحالة: يوجد مشاكل — أصلحها قبل المتابعة")

if __name__ == '__main__':
    verify_dataset(workers_dir='dataset', db_file='worker_db_local.pkl')

    