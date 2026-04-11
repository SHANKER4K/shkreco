import torch
import torch.nn as nn
import torch.nn.functional as F


class IResNetBlock(nn.Module):
    """
    Improved Residual Unit من الورقة البحثية — Figure 3, section 4.

    البنية: BN → Conv → BN → PReLU → Conv → BN (+ skip connection)

    الفرق عن ResNet العادي:
    1. PReLU بدل ReLU — يتعلم معامل سالب لكل channel
    2. BatchNorm قبل كل Conv وبعده — يستقر التدريب أكثر
    3. لا activation في نهاية الـ block — يحافظ على المعلومات
    """

    def __init__(self, channels):
        super().__init__()
        self.block = nn.Sequential(
            nn.BatchNorm2d(channels),
            nn.Conv2d(channels, channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(channels),
            nn.PReLU(channels),   # section 4: "use PReLU as activation"
            nn.Conv2d(channels, channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(channels),
        )
        # Skip connection — الفكرة الأساسية من ResNet (He et al. 2016)
        # تسمح للـ gradient بالمرور مباشرة وتحل مشكلة vanishing gradient
        self.prelu = nn.PReLU(channels)

    def forward(self, x):
        # x + block(x) هو الـ residual connection
        return self.prelu(x + self.block(x))


class DownsampleBlock(nn.Module):
    """
    Block انتقالي بين المراحل — يغير الحجم والـ channels معاً.
    يُستخدم مرة واحدة في بداية كل مرحلة جديدة.
    """

    def __init__(self, in_channels, out_channels, stride=2):
        super().__init__()
        self.block = nn.Sequential(
            nn.BatchNorm2d(in_channels),
            nn.Conv2d(in_channels, out_channels, 3,
                      stride=stride, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.PReLU(out_channels),
            nn.Conv2d(out_channels, out_channels, 3,
                      padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
        )
        # Skip connection مع تعديل الأبعاد
        self.downsample = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 1,
                      stride=stride, bias=False),
            nn.BatchNorm2d(out_channels),
        )
        self.prelu = nn.PReLU(out_channels)

    def forward(self, x):
        return self.prelu(self.downsample(x) + self.block(x))


class ArcFaceBackbone(nn.Module):
    """
    IR-ResNet backbone مبسّط — مستوحى من section 4 في الورقة.

    المدخل:  112×112×3  (ArcFace يستخدم 112 وليس 160 مثل FaceNet)
    المخرج:  512-d embedding مُطبَّق عليه L2 normalize

    البنية (من الورقة جدول 1):
    Input → Conv(64) → Stage1(64,3) → Stage2(128,4)
          → Stage3(256,6) → Stage4(512,3) → BN → FC(512) → BN
    """

    def __init__(self, embedding_dim=512):
        super().__init__()

        # طبقة الدخول — تحويل الصورة لـ feature maps أولية
        self.input_layer = nn.Sequential(
            nn.Conv2d(3, 64, 3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(64),
            nn.PReLU(64),
        )

        # 4 مراحل — كل مرحلة تضاعف الـ channels وتُنصّف الحجم
        # الأرقام (64,3), (128,4)... من جدول 1 في الورقة
        self.stage1 = self._make_stage(64,  64,  n_blocks=3)
        self.stage2 = self._make_stage(64,  128, n_blocks=4)
        self.stage3 = self._make_stage(128, 256, n_blocks=6)
        self.stage4 = self._make_stage(256, 512, n_blocks=3)

        # طبقة الخروج — تحويل feature maps لـ embedding vector
        # بعد stage4: الحجم المكاني = 7×7 لمدخل 112×112
        self.output_layer = nn.Sequential(
            nn.BatchNorm2d(512),
            nn.Flatten(),
            nn.Linear(512 * 7 * 7, embedding_dim, bias=False),
            nn.BatchNorm1d(embedding_dim),
        )

    def _make_stage(self, in_c, out_c, n_blocks):
        """بناء مرحلة: Downsample أولاً ثم n-1 Residual Blocks"""
        layers = [DownsampleBlock(in_c, out_c, stride=2)]
        for _ in range(n_blocks - 1):
            layers.append(IResNetBlock(out_c))
        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.input_layer(x)
        x = self.stage1(x)
        x = self.stage2(x)
        x = self.stage3(x)
        x = self.stage4(x)
        x = self.output_layer(x)
        # L2 normalize — section 3: "we fix ||x||=s on hypersphere"
        return F.normalize(x, p=2, dim=1)