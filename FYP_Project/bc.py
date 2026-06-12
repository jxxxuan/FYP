import torch
import torch.nn.functional as F
from constants import *
from utils.utils import *

# Pseudo-code: Run at the beginning of train() or externally
def behavioral_cloning_pretrain(actor, opt, buffer, iterations=2000):
# def behavioral_cloning_pretrain(model, opt, buffer, iterations=2000):
    print("--- Starting Behavioral Cloning Pre-training (Town04/05) ---")
    actor.train()
    # model.train()

    for i in range(iterations):
        # Sample expert experiences from Town04, Town05 buffer
        # Here we sample the training dataset
        e_s, e_a, _, _, _ = buffer.sample_expert(BC_BATCH_SIZE)
        
        pred_mu, _ = actor(e_s['visual'], e_s['goal'])
        # feat = model.get_feature(e_s['visual'])
        # pred_mu, _ = model.actor(feat, e_s['goal'])
        train_loss = F.mse_loss(torch.tanh(pred_mu), e_a)
        
        opt.zero_grad()
        train_loss.backward()
        opt.step()
