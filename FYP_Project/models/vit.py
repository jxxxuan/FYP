import torch
import torch.nn as nn
from timm.models.vision_transformer import Block

class ViTEncoder(nn.Module):
    def __init__(self, img_size_h, img_size_w, patch_size=14, in_chans=12, embed_dim=256, depth=2, num_heads=1):
        super().__init__()
        self.patch_size = patch_size
        self.num_patches_h = img_size_h // patch_size
        self.num_patches_w = img_size_w // patch_size
        self.num_patches = self.num_patches_h * self.num_patches_w
        
        self.patch_embed = nn.Conv2d(in_chans, embed_dim, kernel_size=patch_size, stride=patch_size)
        
        self.cls_token = nn.Parameter(torch.zeros(1, 1, embed_dim))
        self.pos_embed = nn.Parameter(torch.zeros(1, self.num_patches + 1, embed_dim))
        
        # 3. Transformer Encoder Blocks [cite: 169, 287]
        # Paper specifies using 2 Blocks and 1 Head 
        self.blocks = nn.ModuleList([
            Block(dim=embed_dim, num_heads=num_heads, mlp_ratio=4.0, qkv_bias=True)
            for _ in range(depth)
        ])
        
        self.norm  = nn.LayerNorm(embed_dim)
        
        # 4. Fully Connected Layer (final output is 256-dim) [cite: 170, 187]
        self.head = nn.Linear(embed_dim, embed_dim)

    def forward(self, x):
        # x shape: (Batch, Channels, img_dim, img_dim*3)
        x = self.patch_embed(x)  # (B, 256, 8， 24)
        x = x.flatten(2).transpose(1, 2)  # (B, 192, 256)
        
        # Add Class Token [cite: 125]
        cls_token = self.cls_token.expand(x.shape[0], -1, -1)
        x = torch.cat((cls_token, x), dim=1)  # (B, 193, 256)
        
        # Add position embedding [cite: 123]
        x = x + self.pos_embed
        
        # Pass through Transformer layers [cite: 169, 184]
        for block in self.blocks:
            x = block(x)
            
        x = self.norm(x)
        
        # Extract class token output as image feature H_t [cite: 170, 171]
        return self.head(x[:, 0])