import torch
import gc
import logging
import copy
import progressbar
from training.utils import compute_text_embeddings, compute_time_ids
from training.checkpoint import save_checkpoint
from training.loss import compute_loss

from training.hooks import register_hooks

logger = logging.getLogger(__name__)

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

    velocity_loss_weight = 0.01  

    for epoch in range(first_epoch, args.num_train_epochs):
        unet.train()
        if args.train_text_encoder:
            text_encoder_one.train()
            text_encoder_two.train()

        for step, batch in enumerate(train_dataloader):
            with accelerator.accumulate(unet):
                try:
                    prompts = batch["prompts"]
                    pixel_values = batch["pixel_values"].to(accelerator.device, dtype=vae.dtype)
                    latents = vae.encode(pixel_values).latent_dist.sample() * vae.config.scaling_factor
                    noise = torch.randn_like(latents)
                    timesteps = torch.randint(0, noise_scheduler.config.num_train_timesteps, (latents.shape[0],)).long().to(latents.device)
                    noisy_latents = noise_scheduler.add_noise(latents, noise, timesteps)

                    prompt_embeds, pooled_prompt_embeds = compute_text_embeddings(prompts, text_encoders, tokenizers, accelerator)
                    added_cond_kwargs = {"text_embeds": pooled_prompt_embeds, "time_ids": time_ids}
                    model_output = unet(noisy_latents, timesteps, prompt_embeds, added_cond_kwargs=added_cond_kwargs).sample

                    with torch.no_grad():
                        refer_output = refer_model(noisy_latents, timesteps, prompt_embeds, added_cond_kwargs=added_cond_kwargs).sample

                    target = noise


                    loss_model = compute_loss(model_output, target, noise_scheduler, timesteps, latents)


                    print(f"Step: {step}, Epoch: {epoch}, Loss Model: {loss_model.item()}")


                    if args.dcoloss > 0.0:

                        clamped_timesteps = torch.clamp(timesteps.float().unsqueeze(-1), min=1.0, max=noise_scheduler.config.num_train_timesteps)
                        velocity = (model_output - refer_output) / (clamped_timesteps + 1e-5)

                        ideal_velocity = (target - noisy_latents) / (1 - clamped_timesteps)


                        velocity_loss = torch.norm(velocity - ideal_velocity, dim=-1).mean()


                        print(f"Step: {step}, Epoch: {epoch}, Velocity Loss: {velocity_loss.item()}")


                        loss_refer = compute_loss(refer_output, target, noise_scheduler, timesteps, latents)
                        diff = loss_model - loss_refer


                        inside_term = -1 * args.dcoloss * (diff + velocity_loss_weight * velocity_loss)

                        inside_term = torch.clamp(inside_term, min=-10.0, max=10.0)
                        

                        loss = -1 * torch.nn.LogSigmoid()(inside_term)
                    else:
                        loss = loss_model

                    print(f"Step: {step}, Epoch: {epoch}, Final Loss: {loss.item()}")

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
