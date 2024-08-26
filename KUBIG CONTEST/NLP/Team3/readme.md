## [NLP Team 3] AI 공감의 정상화 (공감형 챗봇 만들기 프로젝트)

## Members
19기 최지우, 20기 윤시호, 이세은

## Introduction
인간적인 공감 능력을 겸비한 챗봇을 직접 구현해보고자 함

## Structure

* 사용한 데이터셋: AI hub 공감형 대화 데이터셋
  
  https://www.aihub.or.kr/aihubdata/data/view.do?currMenu=115&topMenu=100&dataSetSn=71305

* GPT-2 기반 한국어 언어모델인 KoGPT2를 답변 생성 모델로 사용
  - 공감형 대화 데이터셋을 Single-turn 과 Multi-turn 형태로 변환
  - Generate 함수와 후처리를 통해 유저의 감정에 공감해주는 답변을 생성
  - 유저의 텍스트를 입력으로 받아 답변을 생성
    
* 감정라벨 분류 task에 BERT 사용
  - 공감형 대화 데이터셋에서 text와 emotion_label 추출, 라벨 인코딩
  - 문장을 입력하면 그 문장의 감정 라벨을 출력하는 함수 정의
  - 챗봇 응답마다 감정 라벨 이모티콘 매칭


![image](https://github.com/KU-BIG/KUBIG_2024_FALL/blob/main/KUBIG%20CONTEST/NLP/Team3/image/architecture%20diagram.png)

## Results

![image](https://github.com/KU-BIG/KUBIG_2024_FALL/blob/main/KUBIG%20CONTEST/NLP/Team3/chat.png)

* 평가
  - 대체적으로 사람 수준의 공감능력, 대화 문맥 유지, 이모티콘으로 감정적 몰입 부여
  - 특수하고 복잡한 상황에서는 대화 흐름에서 벗어난 답변을 하기도 함
  - 상황에 맞지 않게 지나치게 긍정적 / 현실적인 조언을 해주지 못하는 경우가 존재

* 추후 발전방향
  - Langchain 활용으로 복잡한 대화 인식 및 생성 지원
  - 감정 분류 및 이모티콘 매칭 프로세스 강화

