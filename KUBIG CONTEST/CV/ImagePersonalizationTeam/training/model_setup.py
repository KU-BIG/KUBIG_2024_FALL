import torch
from diffusers import DDPMScheduler, AutoencoderKL, UNet2DConditionModel
from peft import LoraConfig
from utils.text_embeddings import TokenEmbeddingsHandler

#code taken from https://github.com/huggingface/diffusers/blob/main/examples/advanced_diffusion_training/train_dreambooth_lora_sdxl_advanced.py

def setup_models(args, accelerator, tokenizers, text_encoders, data_cfg):
    noise_scheduler = DDPMScheduler.from_pretrained(args.pretrained_model_name_or_path, subfolder="scheduler")
    text_encoder_one, text_encoder_two = text_encoders
    vae_path = args.pretrained_model_name_or_path if args.pretrained_vae_model_name_or_path is None else args.pretrained_vae_model_name_or_path
    vae = AutoencoderKL.from_pretrained(
        vae_path,
        subfolder="vae" if args.pretrained_vae_model_name_or_path is None else None,
        revision=args.revision,
        variant=args.variant,
    )

    unet = UNet2DConditionModel.from_pretrained(
        args.pretrained_model_name_or_path, subfolder="unet", revision=args.revision, variant=args.variant
    )

    if args.train_text_encoder_ti:
        inserting_tokens = data_cfg["inserting_tokens"]
        initializer_tokens = data_cfg["initializer_tokens"]
        
        embedding_handler = TokenEmbeddingsHandler(
            [text_encoder_one, text_encoder_two], tokenizers
        )
        embedding_handler.initialize_new_tokens(
            inserting_tokens=inserting_tokens, 
            initializer_tokens=initializer_tokens
        )
    
    vae.requires_grad_(False)
    text_encoder_one.requires_grad_(False)
    text_encoder_two.requires_grad_(False)
    unet.requires_grad_(False)

    weight_dtype = torch.float32
    if accelerator.mixed_precision == "fp16":
        weight_dtype = torch.float16
    elif accelerator.mixed_precision == "bf16":
        weight_dtype = torch.bfloat16

    unet.to(accelerator.device, dtype=weight_dtype)
    vae.to(accelerator.device, dtype=torch.float32)
    text_encoder_one.to(accelerator.device, dtype=weight_dtype)
    text_encoder_two.to(accelerator.device, dtype=weight_dtype)

    unet_lora_config = LoraConfig(
        r=args.rank,
        lora_alpha=args.rank,
        init_lora_weights="gaussian",
        target_modules=["to_k", "to_q", "to_v", "to_out.0"],
    )
    unet.add_adapter(unet_lora_config)

    if args.train_text_encoder:
        text_lora_config = LoraConfig(
            r=args.rank,
            lora_alpha=args.rank,
            init_lora_weights="gaussian",
            target_modules=["q_proj", "k_proj", "v_proj", "out_proj"],
        )
        text_encoder_one.add_adapter(text_lora_config)
        text_encoder_two.add_adapter(text_lora_config)
    elif args.train_text_encoder_ti:
        text_lora_parameters_one = []
        for name, param in text_encoder_one.named_parameters():
            if "token_embedding" in name:
                param = param.to(dtype=torch.float32)
                param.requires_grad = True
                text_lora_parameters_one.append(param)
            else:
                param.requires_grad = False
        text_lora_parameters_two = []
        for name, param in text_encoder_two.named_parameters():
            if "token_embedding" in name:
                param = param.to(dtype=torch.float32)
                param.requires_grad = True
                text_lora_parameters_two.append(param)
            else:
                param.requires_grad = False

    if accelerator.mixed_precision == "fp16":
        models = [unet]
        if args.train_text_encoder:
            models.extend([text_encoder_one, text_encoder_two])
        for model in models:
            for param in model.parameters():
                if param.requires_grad:
                    param.data = param.to(torch.float32)

    return {
        "vae": vae,
        "unet": unet,
        "text_encoder_one": text_encoder_one,
        "text_encoder_two": text_encoder_two
    }, noise_scheduler
