import torch
import gc
import logging
import copy
import progressbar
import torch.nn.functional as F
from collections import deque
from training.utils import compute_text_embeddings, compute_time_ids
from training.checkpoint import save_checkpoint
from training.loss import compute_loss
from training.hooks import register_hooks

logger = logging.getLogger(__name__)

def downsample_image(image, scale_factor):
    return F.interpolate(image, scale_factor=scale_factor, mode='bilinear', align_corners=False)

def train_loop(args, accelerator, models, noise_scheduler, optimizer, lr_scheduler, train_dataloader, text_encoders, tokenizers):
    vae, unet = models["vae"], models["unet"]
    text_encoder_one, text_encoder_two = models["text_encoder_one"], models["text_encoder_two"]
    embedding_handler = models.get("embedding_handler")

    refer_model = copy.deepcopy(unet)
    for param in refer_model.parameters():
        param.requires_grad = False

    global_step, first_epoch = 0, 0
    logger.info("Start")

    time_ids = compute_time_ids(args, accelerator)
    register_hooks(accelerator, models, args)

    widgets = [
        ' [', progressbar.Percentage(), '] ',
        progressbar.Bar(), ' (', progressbar.ETA(), ') ',
        progressbar.DynamicMessage('loss')
    ]
    progress_bar = progressbar.ProgressBar(max_value=args.max_train_steps, widgets=widgets)
    progress_bar.start()

    noise_strength = 0.0

    scales_low_res = [0.5, 0.75]  # Low-Resolution Scales for loosing term
    scales_high_res = [1.0]       # High-Resolution Scales for winning term
    loosing_output = None

    for epoch in range(first_epoch, args.num_train_epochs):
        unet.train()
        if args.train_text_encoder:
            text_encoder_one.train()
            text_encoder_two.train()

        for step, batch in enumerate(train_dataloader):
            # Process loosing term (low resolution)
            for scale in scales_low_res:
                with accelerator.accumulate(unet):
                    try:
                        prompts = batch["prompts"]
                        pixel_values = downsample_image(batch["pixel_values"].to(accelerator.device, dtype=vae.dtype), scale)
                        latents = vae.encode(pixel_values).latent_dist.sample() * vae.config.scaling_factor
                        noise = torch.randn_like(latents)
                        timesteps = torch.randint(0, noise_scheduler.config.num_train_timesteps, (latents.shape[0],)).long().to(latents.device)
                        noisy_latents = noise_scheduler.add_noise(latents, noise, timesteps)

                        prompt_embeds, pooled_prompt_embeds = compute_text_embeddings(prompts, text_encoders, tokenizers, accelerator)
                        added_cond_kwargs = {"text_embeds": pooled_prompt_embeds, "time_ids": time_ids}

                        model_output_low_res = unet(noisy_latents, timesteps, prompt_embeds, added_cond_kwargs=added_cond_kwargs).sample

                        with torch.no_grad():
                            refer_output_low_res = refer_model(noisy_latents, timesteps, prompt_embeds, added_cond_kwargs=added_cond_kwargs).sample

                            if loosing_output is None:
                                loosing_output = refer_output_low_res.clone()

                        # Resize loosing output to match the model's output size
                        loosing_output = F.interpolate(loosing_output, size=model_output_low_res.shape[-2:], mode='bilinear', align_corners=False)

                        loss_loosing = compute_loss(loosing_output, noise, noise_scheduler, timesteps, latents)
                        loss_refer_low_res = compute_loss(refer_output_low_res, noise, noise_scheduler, timesteps, latents)

                    except Exception as e:
                        logger.error(f"Error at epoch {epoch}, step {step}: {e}")
                        raise

            # Process winning term (high resolution)
            for scale in scales_high_res:
                with accelerator.accumulate(unet):
                    try:
                        pixel_values_high_res = batch["pixel_values"].to(accelerator.device, dtype=vae.dtype)
                        latents_high_res = vae.encode(pixel_values_high_res).latent_dist.sample() * vae.config.scaling_factor
                        noise_high_res = torch.randn_like(latents_high_res)
                        timesteps_high_res = torch.randint(0, noise_scheduler.config.num_train_timesteps, (latents_high_res.shape[0],)).long().to(latents_high_res.device)
                        noisy_latents_high_res = noise_scheduler.add_noise(latents_high_res, noise_high_res, timesteps_high_res)

                        model_output_high_res = unet(noisy_latents_high_res, timesteps_high_res, prompt_embeds, added_cond_kwargs=added_cond_kwargs).sample

                        with torch.no_grad():
                            refer_output_high_res = refer_model(noisy_latents_high_res, timesteps_high_res, prompt_embeds, added_cond_kwargs=added_cond_kwargs).sample

                        loss_model = compute_loss(model_output_high_res, noise_high_res, noise_scheduler, timesteps_high_res, latents_high_res)
                        loss_refer_high_res = compute_loss(refer_output_high_res, noise_high_res, noise_scheduler, timesteps_high_res, latents_high_res)

                        diff_winning = loss_model - loss_refer_high_res
                        diff_loosing = loss_loosing - loss_refer_low_res

                        if torch.abs(diff_loosing) < 1e-8:
                            diff_loosing = 0.0

                        inside_term = -1 * args.dcoloss * (diff_winning - 0.001 * diff_loosing)
                        loss = -1 * torch.nn.LogSigmoid()(inside_term)

                        accelerator.backward(loss)

                        if accelerator.sync_gradients:
                            torch.nn.utils.clip_grad_norm_(unet.parameters(), 1.0)

                        optimizer.step()
                        lr_scheduler.step()
                        optimizer.zero_grad()

                        if accelerator.sync_gradients:
                            global_step += 1
                            progress_bar.update(global_step, loss=loss.item())

                            logs = {"loss": loss.detach().item(), "lr": lr_scheduler.get_last_lr()[0]}
                            accelerator.log(logs, step=global_step)

                            if global_step % args.checkpoint_save == 0:
                                save_checkpoint(accelerator, args, unet, text_encoder_one, text_encoder_two, embedding_handler, global_step)

                        if global_step >= args.max_train_steps:
                            break

                    except Exception as e:
                        logger.error(f"Error at epoch {epoch}, step {step}: {e}")
                        raise

        gc.collect()
        torch.cuda.empty_cache()

    progress_bar.finish()
    logger.info("Training completed")
