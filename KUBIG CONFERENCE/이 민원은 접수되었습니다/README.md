# 청년정책 추천 챗봇

## 프로젝트 개요

청년정책 추천 챗봇은 사용자가 거주지, 나이, 취업 상태 등과 같은 개인 정보를 입력하면 맞춤형 청년정책을 추천해주는 실시간 대화형 챗봇 서비스입니다. 이 프로젝트는 지속적인 대화를 통해 사용자가 복잡한 정책 정보를 쉽게 이해하고, 자신에게 맞는 정책을 간편하게 선택할 수 있도록 돕는 것을 목표로 합니다.

이 챗봇은 대한민국 공식 전자정부 웹사이트인 [온통청년](https://www.youthcenter.go.kr/main.do)의 청년정책 데이터를 기반으로 하여, 지역별, 연령별, 상황에 맞는 정책을 빠르게 제공하며, 정책의 상세한 내용도 함께 안내합니다. Gradio 인터페이스를 사용해 웹 브라우저에서 손쉽게 챗봇을 사용할 수 있으며, 직관적인 대화 형식으로 누구나 쉽게 접근할 수 있습니다.

### 주요 기능

1. 개인 맞춤형 정책 추천

    - 사용자가 거주지, 나이, 취업상태 등의 개인정보를 입력하면 가장 관련성이 높은 정책 추천

    - 유사한 정책 간 비교

2. 정책 세부사항 제공

    - 사용자가 특정한 정책의 신청 기간, 자격 요건, 필수 지원 서류 등을 질문하면 관련 문서에서 해당 내용을 찾아 답변 제공

3. 정책용어 설명

    - 정책 정보에 포함된 어려운 용어에 대한 부가적인 설명 제공

## Project Structure

```
youth_policy
├─ .gitignore
├─ chatbot.py
├─ data
│  ├─ chromadb.py
│  ├─ crawling_words.ipynb
│  ├─ layout_analyzer.py
│  └─ policy_crawling_and_attached_file_save.py
├─ download_db.py
├─ README.md
└─ requirements.txt
```

## Installation

1. **Clone the repository**:

    Clone the repository to your local machine using the following command:

    ```bash
    git clone https://github.com/junhyeok9/youth_policy.git
    ```


2. **Navigate to the project directory**:

    Move into the directory of the cloned repository:

    ```bash
    cd youth_policy
    ```

3. **Install the required packages**:

    Install all the dependencies listed in the ```requirements.txt``` file:

    ```bash
    pip install -r requirements.txt
    ```


## Usage

1. **Download the Chroma DB from Google Drive**:

    Run the ```download_db.py``` script to download the necessary database files.

    ```bash
    python download_db.py
    ```   

2. **Set up API keys in environment variables**:

    Rename the ```.env.example``` file to ```.env```, and add your API keys inside the file.

3. **Run the chatbot**:

    Start the chatbot by running the ```chatbot.py``` script.

    ```bash
    python chatbot.py
    ```

4. **Open the Gradio interface**:

    After running the chatbot, open the Gradio interface in your web browser by navigating to:

    ```
    http://127.0.0.1:7860
    ```

## Pipeline

![pipeline](https://github.com/user-attachments/assets/704f4174-3137-43c1-8555-04de8646358e)

## Example

![example](https://github.com/user-attachments/assets/06e4137f-2012-471d-a3df-2bf065eb4019)

## Authors

This project was created by the following contributors:

- **강민정** 

    - 고려대학교 통계학과 석사

    - 정책용어 크롤링

    - 프롬프트 엔지니어링을 통한 챗봇 성능 개선
    
    - 프로젝트 소개서 작성

- **원준혁**

    - 고려대학교 통계학과 석사

    - 정책정보 크롤링 및 정책 파일 저장
    
    - 크롤링 정보 데이터베이스 저장 및 chunking, embedding

    - 데모 실행 조정 및 비디오 제작

- **이세은**

    - 고려대학교 통계학과 학부

    - SMART-RAG 파이프라인 구축 및 챗봇 실행 코드 작성

    - Gradio를 통한 웹서비스 구현

    - Github repository 정리 및 readme.md 작성


