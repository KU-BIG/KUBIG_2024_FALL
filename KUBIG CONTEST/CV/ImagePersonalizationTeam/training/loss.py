import torch
import torch.nn.functional as F

def compute_loss(model_pred, target, noise_scheduler, timesteps, model_input):
    if noise_scheduler.config.prediction_type == "epsilon":
        target = target
    elif noise_scheduler.config.prediction_type == "v_prediction":
        target = noise_scheduler.get_velocity(model_input, target, timesteps)
    else:
        raise ValueError(f"Unknown prediction type {noise_scheduler.config.prediction_type}")
    loss = F.mse_loss(model_pred.float(), target.float(), reduction="mean")

    return loss
