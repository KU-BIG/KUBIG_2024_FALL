## [NLP Team 3] AI 공감의 정상화(공감형 챗봇 만들기 프로젝트)

## Members
19기 최지우, 20기 윤시호, 이세은

## Introduction
인간적인 공감 능력을 겸비한 챗봇을 직접 구현해보고자 함

## Structure

* GPT-2 기반 한국어 언어모델인 KoGPT2를 답변 생성 모델로 사용
  - 공감형 대화 데이터셋을 Single-turn 과 Multi-turn 형태로 변환
  - Generate 함수와 후처리를 통해 유저의 감정에 공감해주는 답변을 생성
![image](https://github.com/user-attachments/assets/39f0e035-63a2-431c-a5d6-fdda81397582)


![image](https://github.com/KU-BIG/KUBIG_2024_FALL/blob/main/KUBIG%20CONTEST/NLP/Team3/architecture%20diagram.png)

## Results
Private f1 score: 0.6809 (28th)

## Structure
