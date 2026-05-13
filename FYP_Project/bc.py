import torch
import torch.nn.functional as F
from constants import *
from utils.utils import *

# 伪代码：在 train() 函数开头或外部进行
def behavioral_cloning_pretrain(actor, opt, buffer, iterations=2000):
# def behavioral_cloning_pretrain(model, opt, buffer, iterations=2000):
    print("--- Starting Behavioral Cloning Pre-training (Town04/05) ---")
    actor.train()
    # model.train()

    for i in range(iterations):
        # 从 Town04, Town05 的 Buffer 中采样专家经验
        # 这里采样的是训练集数据
        e_s, e_a, _, _, _ = buffer.sample_expert(BC_BATCH_SIZE)
        
        pred_mu, _ = actor(e_s['visual'], e_s['goal'])
        # feat = model.get_feature(e_s['visual'])
        # pred_mu, _ = model.actor(feat, e_s['goal'])
        train_loss = F.mse_loss(torch.tanh(pred_mu), e_a)
        
        opt.zero_grad()
        train_loss.backward()
        opt.step()
