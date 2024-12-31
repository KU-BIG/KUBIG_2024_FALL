# [Dacon] Financial Information AI Search Algorithm Competition

## Introduction
중앙정부 재정 정보의 검색 및 제공 편의성과 활용도를 높이는 질의응답 알고리즘 개발하는 프로젝트. 학습데이터로 제공하는 '재정정보 질의 응답 데이터셋'과 재정 보고서, 예산 설명 자료, 기획재정부 보도자료 등 다양한 재정관련 텍스트 데이터를 활용해 주어진 질문에 대한 정확도가 높은 응답을 제시하는 NLP Algorithm을 개발하는 것이 목표이다. (https://dacon.io/competitions/official/236295/overview/description)

## Members
19기 이동주, 20기 강민정, 이유진

## Flow Chart
![image](https://github.com/user-attachments/assets/3951185e-f430-430d-9dae-b1838937e86d)

## Results
Private f1 score: 0.6809 (Top 8%, 28th)
![image](https://github.com/user-attachments/assets/941c8d54-2f27-453c-a0de-644427011dbf)

## Structure
```
Team5/
│
├── train.py - finetune the pretrained models
├── inference.py - make an inference with tuned models
├── model/ - load the best model
│   ├── adapter_config.json
│   ├── special_tokens_map.json
│   └── ...
└── modules/ - functions and classes required to operate the model
    ├── preprocessing.py
    └── create_db.py
```
