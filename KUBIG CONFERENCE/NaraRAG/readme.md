## 국회 의정활동 지원 RAG 기반 챗봇, NaraRAG
특정 정책/법률 현안에 관련된 논의 내용을 검색하고 시간순 및 이슈별로 정리/요약하여 답변하는 챗봇 개발

### Members
18기 심서현, 19기 최주희, 20기 기광민

### Data Preprocessing
**AIHub에 있는 국회 회의록 기반 지식 검색 데이터 중 라벨링데이터 활용**
- 회의 정보 및 날짜 변수: 회의날짜, 국회 대, 회의명, 회수, 차수, 안건, 법안
- 질문 변수: 질문자 이름, 질문, 질문 키워드
- 답변 변수: 답변자 이름, 문맥, 답변, 답변 키워드
  - 질문자 및 답변자 이름은 이름 + 직책 + 부서 변수를 합한 값
  - 질문, 문맥, 답변은 Alpaca로 요약, 정리된 내용으로 사용
  - 안건, 법안 변수는 세미콜론(;), 콤마(,) 등으로 여러 개가 연결된 형태. 마지막 안건 및 법안만 선택하도록 전처리

### RAG(Retrieval-Augmented Generation)
<img width="939" alt="스크린샷 2024-12-31 오전 11 34 40" src="https://github.com/user-attachments/assets/4c5d8953-0c4a-4da5-896e-f4b179cec009" />

- vectorDB: Chroma
- retriever: Parent-Document Retriever, Multi-Query Retriever
- Embedding 및 LLM 생성 모델: Upstage의 solar-passage, chatUpstage 사용
- 추가 prompt engineering: DB에서 검색된 context에만 기반해서 작성하라 + 최신 흐름부터 시간순으로 정리해라 등의 명령어 작성

### 사용법
단순 streamlit 사용이 아닌 Node.js를 사용한 웹 개발 완료. 
- chat 폴더에 있는 Readme 참고
