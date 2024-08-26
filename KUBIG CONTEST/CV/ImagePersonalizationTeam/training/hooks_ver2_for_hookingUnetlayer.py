from diffusers.utils import convert_state_dict_to_diffusers
from peft.utils import get_peft_model_state_dict
from diffusers import StableDiffusionXLPipeline
import torch

def register_hooks(accelerator, models, args):

    vae = models["vae"]
    unet = models["unet"]
    text_encoders = [models["text_encoder_one"], models["text_encoder_two"]]
    
    refer_model = models["refer_model"]

    unet.coarse_features = None
    unet.fine_features = None
    refer_model.coarse_features = None
    refer_model.fine_features = None

    def save_model_hook(_, __, output_dir):
        if accelerator.is_main_process:
            unet_lora_layers = convert_state_dict_to_diffusers(get_peft_model_state_dict(unet))
            text_encoder_lora_layers = convert_state_dict_to_diffusers(get_peft_model_state_dict(text_encoders[0])) if args.train_text_encoder else None
            text_encoder_2_lora_layers = convert_state_dict_to_diffusers(get_peft_model_state_dict(text_encoders[1])) if args.train_text_encoder else None
            StableDiffusionXLPipeline.save_lora_weights(
                output_dir,
                unet_lora_layers=unet_lora_layers,
                text_encoder_lora_layers=text_encoder_lora_layers,
                
                text_encoder_2_lora_layers=text_encoder_2_lora_layers,
            )

    def load_model_hook(_, input_dir):
        from diffusers.loaders import LoraLoaderMixin
        if args.train_text_encoder:
            LoraLoaderMixin.load_lora_into_text_encoder(input_dir, text_encoder_1=text_encoders[0], text_encoder_2=text_encoders[1])
        LoraLoaderMixin.load_lora_into_unet(input_dir, unet=unet)

    accelerator.register_save_state_pre_hook(save_model_hook)
    accelerator.register_load_state_pre_hook(load_model_hook)

    def extract_coarse_features(module, input, output):
        if isinstance(output, tuple):
            output = output[0]  
        unet.coarse_features = output.clone().detach()
        refer_model.coarse_features = output.clone().detach()
        #print("miccheckonetwo:", unet.coarse_features.shape)


    def extract_fine_features(module, input, output):
        if isinstance(output, tuple):
            output = output[0] 
        unet.fine_features = output.clone().detach()
        refer_model.fine_features = output.clone().detach()
        #print("test:", unet.fine_features.shape)



    unet.down_blocks[0].register_forward_hook(extract_coarse_features)   #coarse
    refer_model.down_blocks[0].register_forward_hook(extract_coarse_features)  #refer모델의 coarse

    
    unet.up_blocks[-1].register_forward_hook(extract_fine_features)     # Fine피쳐
    refer_model.up_blocks[-1].register_forward_hook(extract_fine_features)     # refer 모델의 fine 피쳐