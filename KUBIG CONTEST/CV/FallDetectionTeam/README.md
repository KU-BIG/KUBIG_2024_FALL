# YOLOv10 Custom Object Detection

This repository contains the implementation of **YOLOv10**, a state-of-the-art object detection model. This project is designed to demonstrate custom object detection using YOLOv10 with Python.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
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


Feel free to adjust the content and sections as needed based on any additional information from
```

Additionally, you may need to mount your Google Drive if using Google Colab:

```python
from google.colab import drive
drive.mount('/content/drive')
```

# Usage

Follow these steps to run the YOLOv10 model:

**1. Clone the repository:**

```bash
git clone https://github.com/THU-MIG/yolov10.git
cd yolov10
```

**2. Download the required models and weights.** You can specify the path to download or mount a drive if using a cloud environment like Google Colab.

**3. Run the training or inference scripts:**

```bash
python train.py --data data/custom.yaml --cfg cfg/yolov10.yaml --weights weights/yolov10.pt --epochs 50
```
To run inference on your images or videos:

```bash
python detect.py --source path/to/your/images --weights weights/yolov10.pt
```

# Results

Once the training or inference is complete, results will be saved in the runs/ directory. Here, you can find the output images with detected objects and other performance metrics.

# License

Distributed under the MIT License. See LICENSE for more information.

# Acknowledgments

Thanks to the authors of YOLOv10 for their research and contributions to object detection.
THU-MIG for providing the original repository and codebase.
