<div align="center">
  <h1>Image Personalization Team Project</h1>
  <p>Welcome to the Image Personalization Team project repository! This repository contains the necessary code and guidelines to train and generate personalized images. Follow the steps below to get started.</p>
  
  <h2>Prerequisites</h2>
  <p>Before you begin, ensure you have <code>conda</code> installed on your system. You will need to create a new conda environment and install several dependencies.</p>

  <h3>Clone the Repository</h3>
  <p>First, clone this repository to your local machine:</p>
  <pre><code>git clone https://github.com/KU-BIG/KUBIG_2024_FALL/tree/main/KUBIG%20CONTEST/CV/ImagePersonalizationTeam
cd ImagePersonalizationTeam</code></pre>

  <h3>Set Up Conda Environment</h3>
  <p>Create a new conda environment:</p>
  <pre><code>conda create -n myenv python=3.8
conda activate myenv</code></pre>

  <h3>Install Dependencies</h3>
  <p>Install the required Python packages:</p>
  <pre><code>pip install accelerate>=0.16.0
pip install torchvision
pip install transformers>=4.25.1
pip install ftfy
pip install tensorboard
pip install Jinja2
pip install peft==0.7.0</code></pre>

  <h2>Training the Model</h2>
  <p>To train the model with the default dataset, use the following command:</p>
  <pre><code>accelerate launch main.py --config_dir="dataset/happy/config_1.json" --config_name="fine_tune_happy" --output_dir="./output" --learning_rate=5e-5 --text_encoder_lr=5e-6 --dcoloss=1000 --rank=32 --max_train_steps=2000 --checkpoint_save=5 --seed="0" --train_text_encoder_ti --num_train_epochs=2000</code></pre>

  <h3>Training with Your Own Dataset</h3>
  <p>To train the model with your dataset:</p>
  <ol>
    <li>Place about 5 images of your dataset under the <code>dataset/</code> directory.</li>
    <li>Create a configuration file for your dataset.</li>
    <li>Run the training command as described above.</li>
  </ol>

  <h2>Generating Images</h2>
  <p>To generate images after training, run the following command:</p>
  <pre><code>python inference.py</code></pre>

  <h2>Results</h2>
  <p>Here are some results from our model:</p>
  <img src="https://github.com/user-attachments/assets/7f50b355-c6ff-415f-b50e-d56b22286292" alt="Generated Image">

  <h2>Acknowledgements</h2>
  <p>This project is a reimplementation of the model and concepts presented in the paper:</p>
  <p><strong>"Direct Consistency Optimization for Compositional Text-to-Image Personalization"</strong><br>
  Authors: Kyungmin Lee, Sangkyung Kwak, Kihyuk Sohn, Jinwoo Shin</p>
</div>
