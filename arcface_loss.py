import torch
import torch.nn as nn
import torch.nn.functional as F
import math


class ArcFaceLoss(nn.Module):
    """
    تطبيق مباشر من الورقة البحثية:
    'ArcFace: Additive Angular Margin Loss for Deep Face Recognition'
    Deng et al., CVPR 2019 — https://arxiv.org/abs/1801.07698

    المعادلة الأساسية (eq. 3 في الورقة):
    L = -log( e^(s·cos(θ_yi + m)) / (e^(s·cos(θ_yi+m)) + Σ e^(s·cos(θ_j))) )
    """

    def __init__(self, embedding_dim=512, num_classes=10, s=64.0, m=0.5):
        super().__init__()
        # s = scale factor — section 3.3 في الورقة
        # قيمة 64 مختارة لأن r = e^(B-m)·sin(π/K) ≈ 64 لـ 512-d embeddings
        self.s = s

        # m = angular margin — section 3.1 في الورقة
        # القيمة 0.5 راديان (~28.6 درجة) هي الأفضل حسب جدول 7 في الورقة
        self.m = m

        # W = مصفوفة أوزان الكلاسات — shape: (num_classes, embedding_dim)
        # كل صف يمثل "مركز" كلاس في فضاء الـ embeddings
        # section 3 في الورقة: "we fix the bias b_j=0 and transform
        # the logit as W_j^T·x_i = ||W_j||·||x_i||·cos(θ_j)"
        self.W = nn.Parameter(
            torch.FloatTensor(num_classes, embedding_dim)
        )
        nn.init.xavier_uniform_(self.W)

        # حساب قيم مسبقة لتسريع الحساب وتجنب تكراره
        # cos(m) و sin(m) ثابتان طوال التدريب
        self.cos_m = math.cos(m)   # cos(0.5) ≈ 0.8776
        self.sin_m = math.sin(m)   # sin(0.5) ≈ 0.4794

        # حد الاستقرار العددي — eq. 3 footnote في الورقة
        # عندما θ + m > π، نستخدم تقريباً بديلاً لتجنب قيم سالبة
        self.th = math.cos(math.pi - m)   # cos(π - 0.5) ≈ -0.8776
        self.mm = math.sin(math.pi - m) * m  # sin(π-0.5) * 0.5 ≈ 0.2397

    def forward(self, embeddings, labels):
        """
        embeddings: (batch_size, 512) — مُخرَج الـ backbone بعد L2 normalize
        labels:     (batch_size,)     — رقم الكلاس لكل صورة
        """

        # الخطوة 1: L2 normalize لـ W و embeddings
        # هذا يحوّل حساب W^T·x من dot product إلى cosine similarity
        # section 3: "we normalize both features and weight vectors"
        emb_norm = F.normalize(embeddings, p=2, dim=1)  # (B, 512)
        W_norm   = F.normalize(self.W,      p=2, dim=1)  # (C, 512)

        # الخطوة 2: حساب cos(θ_j) لكل كلاس
        # F.linear(x, W) = x · W^T = shape: (batch_size, num_classes)
        # بعد التطبيع: هذا يعطي cos(θ) بين كل embedding وكل مركز كلاس
        cosine = F.linear(emb_norm, W_norm)
        # clamp لتجنب أخطاء floating point خارج [-1, 1]
        cosine = cosine.clamp(-1 + 1e-7, 1 - 1e-7)

        # الخطوة 3: حساب cos(θ + m) بصيغة المجموع الزاوي
        # cos(θ + m) = cos(θ)·cos(m) - sin(θ)·sin(m)
        # هذا مشتق من قانون مجموع الزوايا في المثلثات
        sine        = torch.sqrt(1.0 - cosine.pow(2))   # sin(θ) = √(1-cos²θ)
        cos_theta_m = cosine * self.cos_m - sine * self.sin_m  # cos(θ+m)

        # الخطوة 4: استقرار عددي — footnote في section 3.2
        # إذا θ + m > π (أي cos(θ) < cos(π-m) = th)
        # نستبدل cos(θ+m) بـ cos(θ) - mm لتجنب القيم الشاذة
        cos_theta_m = torch.where(
            cosine > self.th,
            cos_theta_m,
            cosine - self.mm
        )

        # الخطوة 5: تطبيق الـ margin على الكلاس الصحيح فقط
        # one_hot: مصفوفة أصفار ما عدا موضع الكلاس الصحيح = 1
        one_hot = torch.zeros_like(cosine)
        one_hot.scatter_(1, labels.view(-1, 1).long(), 1.0)

        # للكلاس الصحيح   → استخدم cos(θ + m)  (مع الـ margin)
        # لباقي الكلاسات  → استخدم cos(θ)       (بدون margin)
        logits = one_hot * cos_theta_m + (1.0 - one_hot) * cosine

        # الخطوة 6: تطبيق scale s ثم cross-entropy
        # s يكبّر الـ logits لأن القيم بعد التطبيع صغيرة جداً (بين -1 و 1)
        logits = logits * self.s

        # cross-entropy هي الـ -log(softmax) — تطابق eq. 3 في الورقة
        loss = F.cross_entropy(logits, labels.long())
        return loss