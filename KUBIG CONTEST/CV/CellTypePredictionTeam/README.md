# Hist2ST 모델의 spatial transcriptomics를 활용한 breast tissue의 cell type prediction
팀명: 세포실격
<br>
CV 팀원: 20기 김정찬 / 20기 김영언
<br>
<br>
## Paper
[Hist2ST Paper] (https://pubmed.ncbi.nlm.nih.gov/35849101/) 



<br>
<br>

## Model
딥러닝 기반의 Spatial transcriptomics 모델인 HisT2ST
- Hist2ST 모델의 pretrained check point 활용
### Model Architecture
<img src="https://github.com/aldadobi/Spatial-transcriptomics-with-breast-tissue/blob/main/image.png">

Convmixer module : 패치 단위로 연산을 하며 그 연산을 standard convolution을 통해서 진행 , 이미지 patch 간에 internal relation of 2D vision feature를 찾음

Transformer module : self-attention을 통해 전역적인 공간적 특징과 연결고리를 찾아내는 모듈

Graph neural network : 국소적으로 각 이미지 스팟(패치 X)이 이웃 스팟과 공간적으로 어떤 관계를 갖는 지 찾아내는 network

Zero-Inflated Negative Binomial(ZINB) layer : GNN에서 추출한 feature를 input으로 받는 layer, 데이터에 0 값이 과도하게 많을 때 먼저 샘플이 0인지 아닌지를 결정하고 Negative Binomial 분포를 적용시킴


## Task Definition
### Background
#### 1. Spatial Transcriptomics  
![image](https://github.com/user-attachments/assets/b41c6953-7ea4-4dea-bdaa-57d3e6843a6f)
Spatial Transcriptomics는 조직 내 RNA 발현을 spot별로 분석하여 세포 기능과 질병 메커니즘을 이해하는 데 도움을 주는 기술이며 조직의 구조와 유전자 발현을 동시에 분석할 수 있다.
#### 2. Gene Symbol  
![image](https://github.com/user-attachments/assets/c069058c-4016-45b8-bdd9-99a9158df62d)
Cell type matching을 위해 Sequence → Gene Symbol (Cell Marker) → Cell Type의 흐름을 통해 수행한다. 여기서 Sequence는 RNA의 염기서열 정보를 의미하며, Gene Symbol (Cell Marker)은 특정 세포 유형을 나타내는 유전자 표식자이다. Cell Type은 이러한 세포 마커에 의해 정의되는 세포 유형을 의미하며, Cell Marker 정보는 Cell Marker 데이터베이스와 PanglaoDB에서 다운로드하여 matching에 활용하였다.

### Objective
- **기존의 Flow, Image Cytometry 한계 극복**  
  Flow Cytometry는 cell sorting, Image Cytometry는 morphology 분석에 그쳤으나 이 모델은 동시에 수행 가능하다.
- **Label-free model**  
  Cell sorting을 위해 전문가의 anotation이 필요없다. Spatial transcriptomics 기술을 이용하여 marker gene을 통한 cell matching을 하면 된다.
- **Downstream Task**  
  Cell Type 예측을 통해, Disease detecting, cell-to-cell interaction, trajectory and pseudotime inference, survival analysis과 같은 task 수행 가능하다.


## Dataset
### Reference
 -  human HER2-positive breast tumor ST data https://github.com/almaan/her2st/.
 -  human cutaneous squamous cell carcinoma 10x Visium data (GSE144240).
 -  you can also download all datasets from [here](https://www.synapse.org/#!Synapse:syn29738084/files/)

### Data Preprocessing
Using Scanpy, Remove cells that might have insufficient RNA molecule or doublets, Remove genes that are detected in fewer than 3 cells, considered as noise gene, Remove cells that has high percentage of mitochondrial counts which indicates stressed or dead cells

## Result
Hist2ST 모델의 pretrained check point 활용하여 her2st 데이터 중, gene expression과 img을 사용하였다.   
**Result 1**
![image](https://github.com/user-attachments/assets/729be57f-0aee-430b-a349-48f796af4cc1)
Cell Prediction Accuracy: 0.898  
Cluster Prediction Accuracy: 0.551 (ARI: 0.12)

**Result 2**
![image](https://github.com/user-attachments/assets/c8a5bbf5-5ebc-4144-97ba-3dd30fd60677)
Cell Prediction Accuracy: 0.681  
Cluster Prediction Accuracy: 0.702 (ARI: 0.42)

**Result 3**
![image](https://github.com/user-attachments/assets/c99255da-9258-41ad-8063-d793505f2500)
Cell Prediction Accuracy: 0.983  
Cluster Prediction Accuracy: 0.594 (ARI: 0.03)

## Future Model
Gene Symbol이 아닌 Cell Type 예측 모델 ⇒ 예측 class 감소로 정확도 증가 기대  
**Model 1)** Gene Score 기반의 Cell Type 예측  
**Model 2)** Cluster 예측 (Leiden Clustering)




KUBIG contest
