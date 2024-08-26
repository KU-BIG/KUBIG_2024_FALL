# YOLOv10 Fall Detection

This repository contains the implementation of **YOLOv10**, a state-of-the-art object detection model. 
This project is designed to do fall detection using object detection by YOLOv10.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Train Custom dataset](#trainyourcustomdataset)
- [Results](#results)
- [License](#license)
- [Acknowledgments](#acknowledgments)

# Installation

To get started, clone the repository and install the required packages:

```bash
# Clone the repository
git clone https://github.com/THU-MIG/yolov10.git

# Navigate into the cloned repository directory
cd yolov10

# Install required packages
pip install -r requirements.txt
```

Additionally, you may need to mount your Google Drive if using Google Colab:

```python
from google.colab import drive
drive.mount('/content/drive')
```
We used Google Colab, GPU-T4. 

# Usage

Follow these steps to run the YOLOv10 model:

**1. Clone the repository:**

```bash
git clone https://github.com/THU-MIG/yolov10.git
cd yolov10
```

**2. Download the required models and weights.** 

You can specify the path to download or mount a drive if using a cloud environment like Google Colab.

**3. Run the training or inference scripts:**

To run inference on your images or videos:

```bash
python detect.py --source path/to/your/images --weights weights/yolov10.pt
```

# Train Your Custom Dataset

**1. Prepare Your Dataset:**

We used Roboflow - Fall dataset.
Your dataset should be in the YOLO format (with .txt annotation files for each image, where each line represents an object in the format [class_id, x_center, y_center, width, height] normalized between 0 and 1).

Organize your dataset into the following directory structure:

```kotlin
dataset/
├── train/
│   ├── images/
│   │   ├── image1.jpg
│   │   ├── image2.jpg
│   │   └── ...
│   └── labels/
│       ├── image1.txt
│       └── ...
└── val/
    ├── image/
    │   ├── image1.jpg
    │   ├── image2.jpg
    │   └── ...
    └── lables/
        ├── image1.txt
        └── ...
```

**2. To train your Custom model:**

We trained model in epochs of 100. 
Try this to train your model. 
```bash
python train.py --data data/custom.yaml --cfg cfg/yolov10.yaml --weights weights/yolov10.pt --epochs 50
```
Adjust --epochs based on how long you want to train the model.
You can also adjust other hyperparameters as needed in the cfg/yolov10.yaml file.

**3. Inference with your best.pt model**

Our Best trianed model is in yolov10\runs\detect\train7\weights\best.pt. 

```bash
python detect.py --source /path/to/your/new/images --weights yolov10\runs\detect\train7\weights\best.pt --conf 0.25
```

# Results

Once the training or inference is complete, results will be saved in the runs/detect/ directory. 
Here, you can find the output images with detected objects and other performance metrics.
Our Result is in yolov10\runs\detect\predict7. 

# License

[Aarohi Singla](https://github.com/AarohiSingla/YOLOv10-Custom-Object-Detection.git)
[YOLOv10: Real-Time End-to-End Object Detection](https://arxiv.org/pdf/2405.14458)

# Acknowledgments

Thanks to the authors of YOLOv10 for their research and contributions to object detection.
THU-MIG for providing the original repository and codebase.
