import torch
from diffusers.optimization import get_scheduler
from data.dataset import TrainDataset
from utils.collate import collate_fn

def setup_optimizer_and_scheduler(args, accelerator, models):
    unet = models["unet"]
    text_encoder_one = models["text_encoder_one"]
    text_encoder_two = models["text_encoder_two"]

    optimizer_class = torch.optim.AdamW

    optimizer_params = {
        "betas": (0.9, 0.999),
        "weight_decay": 1e-4,  
        "eps": 1e-8, 
    }

    params_to_optimize = [{"params": list(filter(lambda p: p.requires_grad, unet.parameters())), "lr": args.learning_rate}]
    if args.train_text_encoder or args.train_text_encoder_ti:
        params_to_optimize.append({
            "params": list(filter(lambda p: p.requires_grad, text_encoder_one.parameters())),
            "lr": args.text_encoder_lr if args.text_encoder_lr else args.learning_rate,
            "weight_decay": 1e-4,  
        })
        params_to_optimize.append({
            "params": list(filter(lambda p: p.requires_grad, text_encoder_two.parameters())),
            "lr": args.text_encoder_lr if args.text_encoder_lr else args.learning_rate,
            "weight_decay": 1e-4,  
        })
    
    optimizer = optimizer_class(params_to_optimize, **optimizer_params)
    
    train_dataset = TrainDataset(args)
    train_dataloader = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=args.train_batch,
        shuffle=True,
        collate_fn=lambda examples: collate_fn(examples, args),
        num_workers=1,
    )

    num_update_steps_per_epoch = len(train_dataloader)
    max_train_steps = args.max_train_steps or (args.num_train_epochs * num_update_steps_per_epoch)
    lr_scheduler = get_scheduler(
        "constant",
        optimizer=optimizer,
        num_warmup_steps=0,
        num_training_steps=max_train_steps * accelerator.num_processes,
        num_cycles=1,
        power=1.0,
    )
    

    if args.train_text_encoder:
        accelerator.prepare(
            unet, text_encoder_one, text_encoder_two, optimizer, train_dataloader, lr_scheduler
        )
    else:
        accelerator.prepare(
            unet, optimizer, train_dataloader, lr_scheduler
        )
    
    return optimizer, lr_scheduler, train_dataloader
