import torch

# 1. 查看 PyTorch 编译时对应的 CUDA 版本
print(f"PyTorch 编译 CUDA 版本: {torch.version.cuda}")

# 2. 查看显卡驱动支持的最高 CUDA 版本
print(f"CUDA 是否可用: {torch.cuda.is_available()}")

# 3. 如果可用，查看具体显卡型号
if torch.cuda.is_available():
    print(f"当前显卡: {torch.cuda.get_device_name(0)}")