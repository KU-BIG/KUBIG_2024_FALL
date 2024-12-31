## [NLP Team 4] 허깅페이스야 니땀시 살어야 ##
한국어 표준어-방언 번역기와 방언을 구사하는 챗봇 구현

(번역기와 챗봇... 근데 이제 사투리를 곁들인)

## Members ##
18기 강동헌, 19기 정종락, 20기 김채원

## Introduction ## 
목표 : “ 지역 방언을 사용해 질문에 응답하는 챗봇 개발 ”

<img width="930" alt="image" src="https://github.com/user-attachments/assets/749a732b-5d43-44bd-97cf-3d6968e9f00c">

## Structure ##

다음과 같이 두 task로 분류하여 분석 작업 진행

- Task 1 : “ 표준어 질문 (source) - 사투리 대답 (target) 의 데이터셋으로 챗봇 모델을 학습시킨다.”

- Task 2 :  “ 표준어 질문 (source) - 표준어 대답 (target) 의 데이터셋으로 챗봇 모델을 학습시킨 뒤, 번역 모델을 이용해 표준어 대답을 사투리로 번역한다.”

<img width="543" alt="image" src="https://github.com/user-attachments/assets/eb04104b-0121-4cc6-be26-7548265c7f31">

## Dataset ##
- 한국어 방언 발화 데이터 (AI 허브)
- 일상 대화 데이터 (AI 허브 및 타 챗봇 프로젝트 데이터)

## Model ## 

### 번역 ###
- 최종 모델 : KoBART conditional generative model을 fine-tuning

### 챗봇 ###
- 최종 모델 : KoGPT2 pretrained model을 fine-tuning
<img width="608" alt="image" src="https://github.com/user-attachments/assets/96ac8514-8f91-420e-a880-c4f5a86b3e53">

## Result ##

### 번역 ###

#### 예시: 표준어-제주도
<img width="930" alt="Screenshot 2024-08-28 at 12 09 38 PM" src="https://github.com/user-attachments/assets/f887cec2-3281-48fa-abd0-a95e10466c1e">

#### 예시: 표준어-전라도
<img width = "930" alt = "image" src="https://github.com/user-attachments/assets/016be5ba-b1a1-478a-82ba-8334fd27ce5a">

#### 예시: 표준어-경상도
<img width="930" alt="Screenshot 2024-08-28 at 1 34 00 PM" src="https://github.com/user-attachments/assets/fbd606c9-4f8e-4cd3-8aee-db5aeb2da4ee">

#### 예시: 표준어-충청도
<img width="930" alt="Screenshot 2024-08-28 at 1 35 12 PM" src="https://github.com/user-attachments/assets/977c00ce-1c76-4d8a-9965-9dcd3968679e">

#### 예시: 표준어-강원도
<img width = "930" alt = "image" src="https://github.com/user-attachments/assets/250091a6-0dc5-4add-90ce-5917ff388671">



### 챗봇+번역 ###

#### 예시: 일상대화 + 제주도 사투리, 일상대화 + 충청도 사투리
<img width="930" alt="image" src="https://github.com/user-attachments/assets/7f7bda19-1c92-47e3-8d09-01d4c778bed1">


<img width="930" alt="image" src="https://github.com/user-attachments/assets/b28c2e4b-d6ad-4cef-980e-bf9518fb0ec3">

- 발화 의도에 맞는 답변을 번역된 버전으로 성공적으로 생성함을 확인할 수 있음
  









