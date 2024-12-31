import torch
import os
from utils.text_embeddings import encode_prompt

def setup_accelerator(args):
    from accelerate import Accelerator
    from accelerate.utils import DistributedDataParallelKwargs, ProjectConfiguration

    project_config = ProjectConfiguration(project_dir=args.output_dir, logging_dir=None)
    ddp_kwargs = DistributedDataParallelKwargs(find_unused_parameters=True)

    accelerator = Accelerator(
        mixed_precision="fp16",  
        log_with="wandb", 
        project_config=project_config,
        kwargs_handlers=[ddp_kwargs],
    )
    return accelerator

def setup_logging_and_seed(accelerator, args):
    from accelerate.utils import set_seed
    import wandb

    set_seed(args.seed)
    if accelerator.is_main_process and args.output_dir is not None:
        os.makedirs(args.output_dir, exist_ok=True)
    wandb.init(project=args.wandb_project_name, dir=args.output_dir)

def create_tokenizers(args):
    from transformers import AutoTokenizer

    tokenizer_one = AutoTokenizer.from_pretrained(
        args.pretrained_model_name_or_path, subfolder="tokenizer",
        revision=args.revision, variant=args.variant, use_fast=False
    )

    tokenizer_two = AutoTokenizer.from_pretrained(
        args.pretrained_model_name_or_path, subfolder="tokenizer_2",
        revision=args.revision, variant=args.variant, use_fast=False
    )

    return tokenizer_one, tokenizer_two

def create_text_encoders(args, tokenizers):
    from models.model_utils import import_model_class

    text_encoder_cls_one = import_model_class(args.pretrained_model_name_or_path, args.revision)
    text_encoder_cls_two = import_model_class(args.pretrained_model_name_or_path, args.revision, subfolder="text_encoder_2")

    text_encoder_one = text_encoder_cls_one.from_pretrained(
        args.pretrained_model_name_or_path, subfolder="text_encoder",
        revision=args.revision, variant=args.variant
    )

    text_encoder_two = text_encoder_cls_two.from_pretrained(
        args.pretrained_model_name_or_path, subfolder="text_encoder_2",
        revision=args.revision, variant=args.variant
    )

    return text_encoder_one, text_encoder_two

def compute_text_embeddings(prompt, text_encoders, tokenizers, accelerator):
    with torch.no_grad():
        prompt_embeddings, pooled_embeddings = encode_prompt(text_encoders, tokenizers, prompt)
        prompt_embeddings = prompt_embeddings.to(accelerator.device)
        pooled_embeddings = pooled_embeddings.to(accelerator.device)
    return prompt_embeddings, pooled_embeddings

def compute_time_ids(args, accelerator):
    original_size = (args.resolution, args.resolution)
    target_size = (args.resolution, args.resolution)
    time_ids = list(original_size + (0, 0) + target_size)
    time_ids = torch.tensor([time_ids]).to(accelerator.device, dtype=torch.float32)
    return time_ids
