# Detect-GPT!

## Introduction
GPT를 기반으로 생성된 문서들을 탐지하는 패턴을 발견하고(**detection**) 이 패턴에 존재하는 확률함수를 구현하여 모델에 적용한다(**calculating**).

## Members
19기 심승현, 강지윤, 이동주

## Methods
### Fast-DetectGPT(zero-shot)
- Perturbation에 따른 log likelihood의 차이를 기반으로 ai-generated text를 Detection하는 Detect-GPT에 기반
- Sampling을 활용해 conditional score를 비교하는 방식으로 속도를 개선
- ai-hub의 에세이 글 평가 데이터를 활용해 human-written text와 paraphrased text(일부 생성), generated text(100% ai 생성)을 비교

### BERT Classifier(train+test)
- human-written text는 0, ai-generated text는 1로 labeling하여 학습
- ai-hub의 에세이 글 평가 데이터 활용해 human-written text와 paraphrased text(일부 생성), generated text(100% ai 생성)을 비교

## Results
![image](https://github.com/user-attachments/assets/56f61c7a-7e9d-4e42-a3bc-4acf209903f9)
- **Fast-DetectGPT**는 source model에 대한 의존성이 존재하나 분포를 더 뚜렷하게 구분
- **BERT Classifier**는 학습 데이터에 대한 의존성으로 인해 분포 간 겹침이 많아 탐지 정확도가 제한적
