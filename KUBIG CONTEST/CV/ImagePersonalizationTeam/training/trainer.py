import os
import json
from accelerate import Accelerator
from accelerate.logging import get_logger
from accelerate.utils import set_seed, DistributedDataParallelKwargs, ProjectConfiguration
from transformers import AutoTokenizer
from utils.logging import setup_logging
from models.model_utils import import_model_class
from training.model_setup import setup_models
from training.optimizer_setup import setup_optimizer_and_scheduler
from training.training_loop import train_loop
from training.hooks import register_hooks
from utils.text_embeddings import TokenEmbeddingsHandler

logger = get_logger(__name__)

def train(args):
    if os.getenv('RANK', '0') == '0':
        accelerator_project_config = ProjectConfiguration(project_dir=args.output_dir, logging_dir=None)
        kwargs = DistributedDataParallelKwargs(find_unused_parameters=True)
        accelerator = Accelerator(
            mixed_precision="fp16",  
            log_with="wandb",  
            project_config=accelerator_project_config,
            kwargs_handlers=[kwargs],
        )

        setup_logging(accelerator)

        if args.seed is not None:
            set_seed(args.seed)

        if accelerator.is_main_process:
            if args.output_dir is not None:
                os.makedirs(args.output_dir, exist_ok=True)

        with open(args.config_dir, 'r') as data_config:
            data_cfg = json.load(data_config)[args.config_name]

        tokenizers = [AutoTokenizer.from_pretrained(
            args.pretrained_model_name_or_path,
            subfolder="tokenizer",
            revision=args.revision,
            variant=args.variant,
            use_fast=False,
        ), AutoTokenizer.from_pretrained(
            args.pretrained_model_name_or_path,
            subfolder="tokenizer_2",
            revision=args.revision,
            variant=args.variant,
            use_fast=False,
        )]

        text_encoders = [import_model_class(args.pretrained_model_name_or_path, args.revision).from_pretrained(
            args.pretrained_model_name_or_path, subfolder="text_encoder", revision=args.revision, variant=args.variant
        ), import_model_class(args.pretrained_model_name_or_path, args.revision, subfolder="text_encoder_2").from_pretrained(
            args.pretrained_model_name_or_path, subfolder="text_encoder_2", revision=args.revision, variant=args.variant
        )]

        models, noise_scheduler = setup_models(args, accelerator, tokenizers, text_encoders, data_cfg)
        optimizer, lr_scheduler, train_dataloader = setup_optimizer_and_scheduler(args, accelerator, models)

        register_hooks(accelerator, models, args)

        if args.train_text_encoder_ti:
            embedding_handler = TokenEmbeddingsHandler(text_encoders, tokenizers)
            with open(args.config_dir, 'r') as data_config:
                data_cfg = json.load(data_config)[args.config_name]
                inserting_tokens = data_cfg["inserting_tokens"]
                initializer_tokens = data_cfg["initializer_tokens"]

            embedding_handler.initialize_new_tokens(inserting_tokens, initializer_tokens)
            models["embedding_handler"] = embedding_handler

        try:
            train_loop(args, accelerator, models, noise_scheduler, optimizer, lr_scheduler, train_dataloader, text_encoders, tokenizers)
        except Exception as e:
            print(f"Training error: {e}")
            raise
