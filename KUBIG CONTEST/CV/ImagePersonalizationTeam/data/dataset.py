import json
import torch
from torch.utils.data import Dataset
from torchvision import transforms
from PIL import Image, UnidentifiedImageError
from PIL.ImageOps import exif_transpose
import warnings

class TrainDataset(Dataset):
    def __init__(self, args):
        self.config_dir = args.config_dir
        self.config_name = args.config_name
        self.size = args.resolution
        self.dco_loss_enabled = (args.dcoloss > 0.)
        self.text_encoder_ti_enabled = args.train_text_encoder_ti

        self.instance_images, self.instance_prompts = self.load_images_and_prompts("images", "prompts")

        if self.text_encoder_ti_enabled and self.dco_loss_enabled:
            _, self.base_prompts = self.load_images_and_prompts("images", "base_prompts")

        self.num_instance_images = len(self.instance_images)
        self.dataset_length = self.num_instance_images

        self.image_transforms = self.get_image_transforms()

    def __len__(self):
        return self.dataset_length

    def __getitem__(self, index):
        example = self.prepare_instance_example(index)
        return example

    def load_images_and_prompts(self, images_key, prompts_key):
        with open(self.config_dir, 'r') as data_config:
            data_cfg = json.load(data_config)[self.config_name]
        images = []
        for path in data_cfg[images_key]:
            try:
                img = Image.open(path)
                img.load()  # Ensure the image is fully loaded
                images.append(img)
            except (UnidentifiedImageError, OSError) as e:
                print(f"Failed to load image {path}: {e}")
        prompts = [prompt for prompt in data_cfg[prompts_key]]
        return images, prompts

    def get_image_transforms(self):
        return transforms.Compose([
            transforms.Resize(self.size, interpolation=transforms.InterpolationMode.BILINEAR),
            transforms.RandomCrop(self.size),
            transforms.ToTensor(),
            transforms.Normalize([0.5], [0.5]),
        ])

    def prepare_instance_example(self, index):
        instance_image = exif_transpose(self.instance_images[index % self.num_instance_images])
        if instance_image.mode != "RGB":
            instance_image = instance_image.convert("RGB")

        example = {
            "instance_images": self.image_transforms(instance_image),
            "instance_prompt": self.instance_prompts[index % self.num_instance_images]
        }

        if self.text_encoder_ti_enabled and self.dco_loss_enabled:
            example["base_prompt"] = self.base_prompts[index % self.num_instance_images]

        return example
##for check
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Dataset loader")
    parser.add_argument("--config_dir", type=str, required=True, help="Path to config directory")
    parser.add_argument("--config_name", type=str, required=True, help="Config name")
    parser.add_argument("--resolution", type=int, default=512, help="Image resolution")
    parser.add_argument("--dcoloss", type=float, default=0.0, help="DCO loss value")
    parser.add_argument("--train_text_encoder_ti", action="store_true", help="Train text encoder TI")
    
    args = parser.parse_args()

    warnings.filterwarnings("ignore", category=UserWarning, message="Failed to load image Python extension")

    dataset = TrainDataset(args)

    for idx in range(len(dataset)):
        example = dataset[idx]
        print(f"Index: {idx}, Data: {example}")
