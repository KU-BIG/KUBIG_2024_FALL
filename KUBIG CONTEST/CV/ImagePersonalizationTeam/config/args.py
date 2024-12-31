import argparse
import os

def parse_arguments(input_args=None):
    def add_general_args(parser):
        parser.add_argument("--seed", type=int, default=None, help="A seed for reproducible training.")
        parser.add_argument("--rank", type=int, default=32, help=("The dimension of the LoRA update matrices."))

    def add_pretrained_model_args(parser):
        parser.add_argument("--pretrained_model_name_or_path", type=str, default="stabilityai/stable-diffusion-xl-base-1.0")
        parser.add_argument("--pretrained_vae_model_name_or_path", type=str, default="madebyollin/sdxl-vae-fp16-fix")
        parser.add_argument("--revision", type=str, default=None)
        parser.add_argument("--variant", type=str, default=None)

    def add_data_config_args(parser):
        parser.add_argument("--config_dir", type=str, default="")
        parser.add_argument("--config_name", type=str, default="")

    def add_save_args(parser):
        parser.add_argument("--output_dir", type=str, default="outdir", help="The output directory where the model predictions and checkpoints will be written.")
        parser.add_argument("--checkpoint_save", type=int, default=500, help="Save a checkpoint of the training state every X updates")
    
    def add_optimizer_args(parser):
        parser.add_argument("--learning_rate", type=float, default=5e-5, help="Initial learning rate (after the potential warmup period) to use.")
        parser.add_argument("--text_encoder_lr", type=float, default=5e-6, help="Text encoder learning rate to use.")
    parser = argparse.ArgumentParser(description="Simple example of a training script.")


    def add_dataloader_args(parser):
        parser.add_argument("--resolution", type=int, default=1024, help="The resolution for input images, all the images in the train/validation dataset will be resized to this")
        parser.add_argument("--train_batch", type=int, default=1, help="Batch size (per device) for the training dataloader.")
        parser.add_argument("--num_train_epochs", type=int, default=100)
        parser.add_argument("--max_train_steps", type=int, default=1000, help="Total number of training steps to perform.  If provided, overrides num_train_epochs.")
    #added dcoloss        
    def add_training_args(parser):
        parser.add_argument("--dcoloss", type=float, default=1000, help="dcoloss")
        parser.add_argument("--train_text_encoder_ti", action="store_true", help=("Whether to use textual inversion"))
        parser.add_argument("--train_text_encoder", action="store_true", help="Whether to train the text encoder. If set, the text encoder should be float32 precision.")
    add_general_args(parser)    
    add_pretrained_model_args(parser)
    add_data_config_args(parser)
    add_save_args(parser)
    add_dataloader_args(parser)
    add_optimizer_args(parser)
    add_training_args(parser) 
    
    args = parser.parse_args(input_args) if input_args else parser.parse_args()
    
    env_local_rank = int(os.environ.get("LOCAL_RANK", -1))
    if env_local_rank != -1 and env_local_rank != args.local_rank:
        args.local_rank = env_local_rank

    return args
