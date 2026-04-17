import torch
import torch.nn.functional as F
from constants import *
from utils.utils import *

# 伪代码：在 train() 函数开头或外部进行
def behavioral_cloning_pretrain(actor, actor_opt, writer, buffer, device, iterations=1000):
    print("--- Starting Behavioral Cloning Pre-training ---")
    actor.train()
    best_val_loss = float('inf')
    buffer.split_expert_data(val_ratio=0.1)
    
    for i in range(iterations):
        e_s, e_a, _, _, _ = buffer.sample_expert_only(E_BATCH_SIZE)
        pred_mu, _ = actor(e_s['visual'], e_s['goal'])
        train_loss = F.mse_loss(torch.tanh(pred_mu), e_a)
        
        actor_opt.zero_grad()
        train_loss.backward()
        actor_opt.step()

        writer.add_scalar('BC/Train Loss', train_loss.item(), i)

        # --- 每 100 次迭代做一次验证集检查 ---
        if i % 100 == 0:
            val_loss = validate(actor, buffer.get_val_loader(), device) 
            writer.add_scalar('BC/Val Loss', val_loss, i)
            print(f"Iter {i}: Train Loss {train_loss.item():.6f}, Val Loss {val_loss:.6f}")
            
            # 如果验证集 Loss 是历史最低，就保存这个“最聪明”的权重
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                torch.save(actor.state_dict(), "best_bc_model.pth")
                print(">>> Saved best pre-trained model")

            # 提前停止（Early Stopping）可选：
            # 如果连续 5 次验证 Loss 都不降反升，就 break 循环，防止过拟合
    
@torch.no_grad()
def validate(actor, val_loader, device):
    actor.eval()
    total_val_loss = 0
    
    for batch in val_loader:
        # 假设 val_loader 返回 (visual, goal, action, ...)
        obs_v, obs_g, expert_a = batch[0], batch[1], batch[2]
        
        # 调用批处理预处理
        v, g = preprocess_obs(obs_v, obs_g, device)
        expert_a = expert_a.to(device).float()
        
        # 前向传播
        pred_mu, _ = actor(v, g)
        
        # 计算 Loss [cite: 112, 113]
        loss = F.mse_loss(torch.tanh(pred_mu), expert_a)
        total_val_loss += loss.item()
    
    avg_loss = total_val_loss / len(val_loader)
    actor.train()
    return avg_loss