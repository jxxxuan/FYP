import torch
import torch.nn.functional as F
from constants import *
from utils.utils import *

# 伪代码：在 train() 函数开头或外部进行
def behavioral_cloning_pretrain(actor, actor_opt, writer, buffer, val_data, iterations=2000):
    print("--- Starting Behavioral Cloning Pre-training (Town04/05 -> Town03) ---")
    actor.train()
    best_val_loss = float('inf')
    
    # 增加一个早停计数器
    patience = 5 
    no_improve_count = 0

    for i in range(iterations):
        # 从 Town04, Town05 的 Buffer 中采样专家经验
        # 这里采样的是训练集数据
        e_s, e_a, _, _, _ = buffer.sample_expert(BC_BATCH_SIZE)
        
        pred_mu, _ = actor(e_s['visual'], e_s['goal'])
        train_loss = F.mse_loss(torch.tanh(pred_mu), e_a)
        
        actor_opt.zero_grad()
        train_loss.backward()
        actor_opt.step()

        writer.add_scalar('BC/Train Loss', train_loss.item(), i)

        # --- 验证集检查 (Town03) ---
        # if i % 100 == 0:
        #     val_loss = validate(actor, val_data) 
        #     writer.add_scalar('BC/Val Loss', val_loss, i)
        #     print(f"Iter {i}: Train {train_loss.item():.6f}, Val(Town03) {val_loss:.6f}")
            
        #     # 保存最能泛化到 Town03 的权重
        #     if val_loss < best_val_loss:
        #         best_val_loss = val_loss
        #         save_best_actor(actor, actor_opt, i)
        #         no_improve_count = 0
        #     else:
        #         no_improve_count += 1

        #     # 早停逻辑：如果验证集 Loss 连续 500 次迭代不降，说明开始过拟合了
        #     if no_improve_count >= patience:
        #         print(f"Early stopping at iteration {i} to prevent overfitting.")
        #         break
    
@torch.no_grad()
@torch.no_grad()
def validate(actor, val_data):
    """
    使用一次性加载的 Town03 数据进行验证
    """
    if val_data is None:
        return 0.0
    
    actor.eval()
    
    # 直接获取全量验证数据
    v = val_data['state']['visual'] # 已经是 float 且归一化过的
    g = val_data['state']['goal']
    expert_a = val_data['action']
    
    # 前向传播 (如果显存压力大，这里可以分批跑，但 Town03 一般没问题)
    pred_mu, _ = actor(v, g)
    
    # 计算 MSE Loss
    # 注意：论文中输出通常经过 tanh 限制在 [-1, 1]
    loss = F.mse_loss(torch.tanh(pred_mu), expert_a)
    
    actor.train()
    return loss.item()