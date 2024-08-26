## [NLP Team 3] AI 공감의 정상화(공감형 챗봇 만들기 프로젝트)

## Members
19기 최지우, 20기 윤시호, 이세은

## Introduction
인간적인 공감 능력을 겸비한 챗봇을 직접 구현해보고자 함

## Structure

* GPT-2 기반 한국어 언어모델인 KoGPT2를 답변 생성 모델로 사용
  - 공감형 대화 데이터셋을 Single-turn 과 Multi-turn 형태로 변환
  - Generate 함수와 후처리를 통해 유저의 감정에 공감해주는 답변을 생성
  - 유저의 텍스트를 입력으로 받아 답변을 생성
    
* 감정라벨 분류 task에 BERT 사용
  - 공감형 대화 데이터셋에서 text와 emotion_label 추출, 라벨 인코딩
  - 문장을 입력하면 그 문장의 감정 라벨을 출력하는 함수 정의
  - 감정 라벨 이모티콘 매칭


![image](https://github.com/KU-BIG/KUBIG_2024_FALL/blob/main/KUBIG%20CONTEST/NLP/Team3/architecture%20diagram.png)

## Results
Private f1 score: 0.6809 (28th)

## Structure
