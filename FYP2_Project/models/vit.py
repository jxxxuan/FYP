import torch
import torch.nn as nn
from timm.models.vision_transformer import Block

class ViTEncoder(nn.Module):
    def __init__(self, img_size_h, img_size_w, patch_size=16, in_chans=3, embed_dim=256, depth=2, num_heads=1):
        super().__init__()
        self.patch_size = patch_size
        # 计算 Patch 数量: (84/14)^2 = 6 * 6 = 36 [cite: 121]
        self.num_patches_h = img_size_h // patch_size
        self.num_patches_w = img_size_w // patch_size
        self.num_patches = self.num_patches_h * self.num_patches_w
        
        # 1. Linear Projection of Flattened Patches [cite: 123, 178]
        self.patch_embed = nn.Conv2d(in_chans, embed_dim, kernel_size=patch_size, stride=patch_size)
        
        # 2. Learnable Class Token & Position Embedding [cite: 123, 125]
        self.cls_token = nn.Parameter(torch.zeros(1, 1, embed_dim))
        self.pos_embed = nn.Parameter(torch.zeros(1, self.num_patches + 1, embed_dim))
        
        # 3. Transformer Encoder Blocks [cite: 169, 287]
        # 论文指定使用 2 个 Block 和 1 个 Head 
        self.blocks = nn.ModuleList([
            Block(dim=embed_dim, num_heads=num_heads, mlp_ratio=4.0, qkv_bias=True)
            for _ in range(depth)
        ])
        
        self.norm  = nn.LayerNorm(embed_dim)
        
        # 4. Fully Connected Layer (最终输出 256 维) [cite: 170, 187]
        self.head = nn.Linear(embed_dim, embed_dim)

    def forward(self, x):
        # x shape: (Batch, Channels, img_dim, img_dim*3)
        x = self.patch_embed(x)  # (B, 256, 8， 24)
        x = x.flatten(2).transpose(1, 2)  # (B, 192, 256)
        
        # 添加 Class Token [cite: 125]
        cls_token = self.cls_token.expand(x.shape[0], -1, -1)
        x = torch.cat((cls_token, x), dim=1)  # (B, 193, 256)
        
        # 加入位置编码 [cite: 123]
        x = x + self.pos_embed
        
        # 通过 Transformer 层 [cite: 169, 184]
        for block in self.blocks:
            x = block(x)
            
        x = self.norm(x)
        
        # 提取 Class Token 的输出作为图像特征 H_t [cite: 170, 171]
        return self.head(x[:, 0])