## Overview
This repository is based on the original **[LAMP](https://github.com/RQ-Wu/LAMP)** repository. While the original model focuses on learning motion, we have adapted it to learn **camera trajectories** by modifying the loss function and replacing the datasets.

### Key Modifications
- **Loss Function**: Adjusted to better suit camera trajectory learning.
- **Dataset**: Replaced the original dataset with one tailored for camera trajectory training.

---

## Preparation and Pretrained Models
For detailed guidance on preparation steps and pretrained models, please refer to the original [LAMP repository](https://github.com/RQ-Wu/LAMP).

## Additional preparation
For camera trajectory data preparation, run dataset.py 
This python file is automated video dataset download code. 

## To run the code
python exp_run1.py --config configs/camera.yaml
python exp_run2.py --config configs/camera.yaml

These two python file uses different loss function
---

## Acknowledgments
This repository is a modification of the **[LAMP](https://github.com/RQ-Wu/LAMP)** repository. We extend our gratitude to the original authors for their outstanding work and contributions to the field.
