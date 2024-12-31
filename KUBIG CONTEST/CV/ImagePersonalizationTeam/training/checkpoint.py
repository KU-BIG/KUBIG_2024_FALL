import os
import shutil
from safetensors.torch import save_file

def save_checkpoint(accelerator, args, _, __, ___, embedding_handler, global_step):
    if accelerator.is_main_process:
        save_path = os.path.join(args.output_dir, f"checkpoint-{global_step}")
        accelerator.save_state(save_path)

        if args.train_text_encoder_ti:
            embedding_handler.save_embeddings(f"{save_path}/learned_embeds.safetensors")
