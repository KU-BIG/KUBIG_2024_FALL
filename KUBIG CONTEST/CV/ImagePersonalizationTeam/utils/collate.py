import torch

def collate_fn(examples, args):
    pixel_values = [example["instance_images"] for example in examples]
    prompts = [example["instance_prompt"] for example in examples]
    
    if args.train_text_encoder_ti and (args.dcoloss> 0.):
        base_prompts = [example["base_prompt"] for example in examples]

    pixel_values = torch.stack(pixel_values)
    pixel_values = pixel_values.to(memory_format=torch.contiguous_format).float()

    batch = {"pixel_values": pixel_values, "prompts": prompts}
    if args.train_text_encoder_ti and (args.dcoloss> 0.0):
        batch.update({"base_prompts": base_prompts})
    return batch
