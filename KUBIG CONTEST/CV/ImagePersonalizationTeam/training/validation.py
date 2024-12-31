import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
import numpy as np

def run_validation(args, accelerator, models, global_step):
    vae, unet = models["vae"], models["unet"]
    text_encoders = [models["text_encoder_one"], models["text_encoder_two"]]

    if args.validation_prompt and args.num_validation_images > 0:
        try:
            print("Validation process started")
            text_encoder_one, text_encoder_two = (encoder.from_pretrained(
                args.pretrained_model_name_or_path, subfolder=subfolder,
                revision=args.revision, variant=args.variant
            ) for encoder, subfolder in zip(text_encoders, ["text_encoder", "text_encoder_2"]))

            pipeline = StableDiffusionXLPipeline.from_pretrained(
                args.pretrained_model_name_or_path,
                vae=vae,
                text_encoder=accelerator.unwrap_model(text_encoder_one),
                text_encoder_2=accelerator.unwrap_model(text_encoder_two),
                unet=accelerator.unwrap_model(unet),
                revision=args.revision, variant=args.variant,
                torch_dtype=torch.float32,
            )

            scheduler_args = {}
            if "variance_type" in pipeline.scheduler.config:
                variance_type = pipeline.scheduler.config.variance_type
                scheduler_args = {"variance_type": "fixed_small" if variance_type in ["learned", "learned_range"] else variance_type}
                pipeline.scheduler = DPMSolverMultistepScheduler.from_config(pipeline.scheduler.config, **scheduler_args)

            pipeline.to(accelerator.device)
            generator = torch.manual_seed(args.seed) if args.seed else None

            images = [pipeline(prompt=args.validation_prompt, generator=generator).images[0] for _ in range(args.num_validation_images)]
            np_images = np.array([np.asarray(img) for img in images])

            for tracker in accelerator.trackers:
                if tracker.name == "tensorboard":
                    tracker.writer.add_images("validation", np_images, global_step, dataformats="NHWC")

            del pipeline
            torch.cuda.empty_cache()
            print("Validation process completed")
        except Exception as e:
            print(f"Validation error: {e}")
            raise
