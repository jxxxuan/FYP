from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
from torchvision import transforms, datasets, models
import torch.nn as nn
import torch
from gymnasium import spaces

# ----------------------------
# 1) Basic building blocks
# ----------------------------
class ConvBNAct(nn.Module):
    def __init__(self, in_ch, out_ch, kernel=3, stride=1, padding=None,
                 groups=1, norm='bn', act='relu'):
        super().__init__()
        if padding is None:
            padding = kernel // 2
        self.conv = nn.Conv2d(in_ch, out_ch, kernel, stride, padding, groups=groups, bias=False)
        if norm == 'bn':
            self.norm = nn.BatchNorm2d(out_ch)
        elif norm == 'gn':
            self.norm = nn.GroupNorm(32, out_ch)
        else:
            self.norm = nn.Identity()
        if act == 'relu':
            self.act = nn.ReLU(inplace=True)
        elif act == 'swish':
            self.act = nn.SiLU(inplace=True)
        else:
            self.act = nn.Identity()

    def forward(self, x):
        return self.act(self.norm(self.conv(x)))

class SEBlock(nn.Module):
    def __init__(self, channels, reduction=16):
        super().__init__()
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Sequential(
            nn.Linear(channels, channels // reduction, bias=False),
            nn.ReLU(inplace=True),
            nn.Linear(channels // reduction, channels, bias=False),
            nn.Sigmoid()
        )
    def forward(self, x):
        b, c, _, _ = x.size()
        y = self.pool(x).view(b, c)
        y = self.fc(y).view(b, c, 1, 1)
        return x * y

class Bottleneck(nn.Module):
    def __init__(self, in_ch, out_ch, expansion=4, stride=1, use_se=False,
                 dw=False, norm='bn', act='relu', drop_connect=0.0):
        super().__init__()
        mid = out_ch // expansion
        # 1x1 reduce
        self.conv1 = ConvBNAct(in_ch, mid, kernel=1, stride=1, norm=norm, act=act)
        # 3x3 conv (depthwise optional)
        if dw:
            self.conv2 = ConvBNAct(mid, mid, kernel=3, stride=stride, groups=mid, norm=norm, act=act)
            # pointwise to expand
            self.conv3 = ConvBNAct(mid, out_ch, kernel=1, stride=1, norm=norm, act='identity')
        else:
            self.conv2 = ConvBNAct(mid, mid, kernel=3, stride=stride, norm=norm, act=act)
            self.conv3 = ConvBNAct(mid, out_ch, kernel=1, stride=1, norm=norm, act='identity')
        self.use_se = use_se
        if use_se:
            self.se = SEBlock(out_ch)
        self.act = nn.ReLU(inplace=True)
        self.downsample = None
        if stride != 1 or in_ch != out_ch:
            self.downsample = ConvBNAct(in_ch, out_ch, kernel=1, stride=stride, norm=norm, act='identity')
        self.drop_connect = drop_connect

    def forward(self, x):
        identity = x
        out = self.conv1(x)
        out = self.conv2(out)
        out = self.conv3(out)
        if self.use_se:
            out = self.se(out)

        if self.downsample is not None:
            identity = self.downsample(identity)

        if self.training and self.drop_connect > 0.0:
            # simple drop connect implementation
            if torch.rand(1).item() < self.drop_connect:
                out = torch.zeros_like(out)
        out = self.act(out + identity)
        return out

class CNN(nn.Module):
    def __init__(self, num_classes=1000, in_ch=3,
                 widths=[64, 128, 256, 512], depths=[2,2,3,2],
                 bottleneck_expansion=4, use_se=True, dw=False,
                 norm='bn', act='swish', drop_rate=0.2, drop_connect=0.0,
                 pretrained_backbone=None):
        super().__init__()
        # optional: let user plug in pretrained backbone (resnet/efficientnet)
        if pretrained_backbone is not None:
            # e.g., 'resnet50', 'efficientnet_b0'
            try:
                backbone = getattr(models, pretrained_backbone)(pretrained=True)
            except Exception:
                backbone = models.resnet50(pretrained=True)
            # strip classifier
            if hasattr(backbone, 'fc'):
                in_features = backbone.fc.in_features
                backbone.fc = nn.Identity()
            else:
                in_features = widths[-1]
            self.backbone = backbone
            self.classifier = nn.Sequential(
                nn.Dropout(drop_rate),
                nn.Linear(in_features, num_classes)
            )
            return

        # stem
        self.stem = nn.Sequential(
            ConvBNAct(in_ch, widths[0], kernel=3, stride=2, norm=norm, act=act),
            ConvBNAct(widths[0], widths[0], kernel=3, stride=1, norm=norm, act=act)
        )

        # stages
        stages = []
        in_channels = widths[0]
        for idx, (w, d) in enumerate(zip(widths, depths)):
            blocks = []
            for i in range(d):
                stride = 2 if (i == 0 and idx != 0) else 1
                blocks.append(Bottleneck(in_channels, w, expansion=bottleneck_expansion,
                                         stride=stride, use_se=use_se, dw=dw,
                                         norm=norm, act=act, drop_connect=drop_connect))
                in_channels = w
            stages.append(nn.Sequential(*blocks))
        self.stages = nn.ModuleList(stages)

        # head
        self.global_pool = nn.AdaptiveAvgPool2d(1)
        self.dropout = nn.Dropout(drop_rate)
        self.fc = nn.Linear(widths[-1], num_classes)

        # weight init
        self._init_weights()

    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, nonlinearity='relu')
            elif isinstance(m, (nn.BatchNorm2d, nn.GroupNorm)):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.trunc_normal_(m.weight, std=0.02)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)

    def forward(self, x):
        if hasattr(self, 'backbone'):
            feat = self.backbone(x)
            return self.classifier(feat)

        x = self.stem(x)
        for stage in self.stages:
            x = stage(x)
        x = self.global_pool(x).flatten(1)
        x = self.dropout(x)
        return self.fc(x)

class CNNPolicy(BaseFeaturesExtractor):
    def __init__(self,observation_space: spaces.Box, modules, features_dim: int = 256):
        super().__init__(observation_space, features_dim)
        n_input_channels = observation_space.shape[0]
        self.cnn = CNN(num_classes=features_dim, in_ch=n_input_channels)
        self._features_dim = features_dim

    def forward(self, observations: torch.Tensor) -> torch.Tensor:
        return self.cnn(observations)


policy_kwargs = {
        'features_extractor_class':CNNPolicy,
        'features_extractor_kwargs':{'features_dim':256},
    }

model = PPO("MlpPolicy", env, policy_kwargs=policy_kwargs, verbose=1,n_steps=4096)