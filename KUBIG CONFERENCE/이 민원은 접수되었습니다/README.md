# 숨은 정책 찾기 - 청년 정책 특화 대화형 AI 챗봇 서비스

## 프로젝트 개요

"청년 정책 특화 대화형 AI 챗봇"은 사용자에게 맞춤형 청년정책을 추천하고, 방대한 정책 정보를 정확하고 신속하게 제공하는 챗봇 서비스입니다. 지속적인 대화를 통해 사용자가 복잡한 정책 정보를 쉽게 이해하고, 자신에게 맞는 정책을 간편하게 선택할 수 있도록 돕는 것을 목표로 합니다.

이 챗봇은 대한민국 공식 전자정부 웹사이트인 [온통청년](https://www.youthcenter.go.kr/main.do)의 청년정책 데이터를 기반으로 하여, 지역별, 연령별, 상황에 맞는 정책을 빠르게 제공하며, 정책의 상세한 내용도 함께 안내합니다. Streamlit 인터페이스를 사용해 웹 브라우저에서 손쉽게 챗봇을 사용할 수 있으며, 직관적인 대화 형식으로 누구나 쉽게 접근할 수 있습니다.

### 주요 기능

1. 개인 맞춤형 정책 추천

    - 사용자가 거주지, 나이, 취업상태 등의 개인정보를 입력하면 가장 관련성이 높은 정책 추천

    - 유사한 정책 간 비교

    ![ex1](https://github.com/KU-BIG/KUBIG_2024_FALL/blob/46193e797f9a55692ca0ca848e87419b5461ebde/KUBIG%20CONFERENCE/%EC%9D%B4%20%EB%AF%BC%EC%9B%90%EC%9D%80%20%EC%A0%91%EC%88%98%EB%90%98%EC%97%88%EC%8A%B5%EB%8B%88%EB%8B%A4/image/example1.png)


2. 정책 세부사항 제공

    - 사용자가 특정한 정책의 신청 자격, 기간 등을 질문하면 관련 문서에서 해당 내용을 찾아 정확한 답변 제공

    ![ex2](https://github.com/KU-BIG/KUBIG_2024_FALL/blob/9f6f66195fc23bedeb1cbe66f4b41e9191d57dda/KUBIG%20CONFERENCE/%EC%9D%B4%20%EB%AF%BC%EC%9B%90%EC%9D%80%20%EC%A0%91%EC%88%98%EB%90%98%EC%97%88%EC%8A%B5%EB%8B%88%EB%8B%A4/image/example2.png)

3. 정책 용어 의미 설명

    - 사용자가 정책 정보에 포함된 특정한 용어의 의미를 질문하면 이해하기 쉽게 설명
  
    ![ex3](https://github.com/KU-BIG/KUBIG_2024_FALL/blob/ad9b0df08bbb24fd9ed59f8b8607f97020f08966/KUBIG%20CONFERENCE/%EC%9D%B4%20%EB%AF%BC%EC%9B%90%EC%9D%80%20%EC%A0%91%EC%88%98%EB%90%98%EC%97%88%EC%8A%B5%EB%8B%88%EB%8B%A4/image/example3.png)
  
4. 실제 후기 요약

    - 사용자가 특정 정책의 이용 후기를 질문하면 네이버 블로그에서 후기를 검색하여 요약 제공
  
    ![ex4](https://github.com/KU-BIG/KUBIG_2024_FALL/blob/778fcd1574d416bf2a5e58a7d59937d453c4f32e/KUBIG%20CONFERENCE/%EC%9D%B4%20%EB%AF%BC%EC%9B%90%EC%9D%80%20%EC%A0%91%EC%88%98%EB%90%98%EC%97%88%EC%8A%B5%EB%8B%88%EB%8B%A4/image/example4.png)   

## Project Structure

```
youth_policy
├─ chatbot_Self_RAG.ipynb
├─ chatbot_Smart_RAG.py
├─ data
│  ├─ chromadb_before.py
│  ├─ chromadb_new.ipynb
│  ├─ layout_analyzer.py
│  ├─ policy_crawling_and_attached_file_save.py
│  └─ words_crawling.ipynb
├─ README.md
└─ streamlit.ipynb
```

## Pipeline - Self RAG

![pipeline1](https://github.com/KU-BIG/KUBIG_2024_FALL/blob/4d9a40501fef44e99d34ed7f55018a478eff6bad/KUBIG%20CONFERENCE/%EC%9D%B4%20%EB%AF%BC%EC%9B%90%EC%9D%80%20%EC%A0%91%EC%88%98%EB%90%98%EC%97%88%EC%8A%B5%EB%8B%88%EB%8B%A4/image/pipeline_Self_RAG.png)

## Pipeline - Smart RAG

![pipeline2](https://github.com/KU-BIG/KUBIG_2024_FALL/blob/4d9a40501fef44e99d34ed7f55018a478eff6bad/KUBIG%20CONFERENCE/%EC%9D%B4%20%EB%AF%BC%EC%9B%90%EC%9D%80%20%EC%A0%91%EC%88%98%EB%90%98%EC%97%88%EC%8A%B5%EB%8B%88%EB%8B%A4/image/pipeline_Smart_RAG.png)

## Authors

- **강민정** 

    - 고려대학교 통계학과 석사

- **원준혁**

    - 고려대학교 통계학과 석사

- **이세은**

    - 고려대학교 통계학과 학부
