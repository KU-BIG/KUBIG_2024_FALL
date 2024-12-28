from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_upstage import UpstageEmbeddings
from langchain_upstage import ChatUpstage
from langchain_upstage import GroundednessCheck
from langchain_chroma import Chroma
from langchain.docstore.document import Document
from langgraph.graph import END, StateGraph
from langchain_community.retrievers import TavilySearchAPIRetriever
import os
import warnings
warnings.filterwarnings("ignore")
from IPython import get_ipython
from dotenv import load_dotenv
from typing import TypedDict
from typing import List
import gradio as gr


# 환경 변수 이름을 정의
API_KEYS = {
    "UPSTAGE_API_KEY": None,
    "LANGCHAIN_API_KEY": None,
    "TAVILY_API_KEY": None
}


''' 환경 변수를 로드하는 함수 정의 '''
def load_env():
    # running in Google Colab
    if "google.colab" in str(get_ipython()):
        from google.colab import userdata
        for key in API_KEYS.keys():
            API_KEYS[key] = os.environ.setdefault(key, userdata.get(key))

    # running in local Jupyter Notebook
    else:
        load_dotenv()  # .env 파일을 로드
        for key in API_KEYS.keys():
            API_KEYS[key] = os.environ.get(key)

    return tuple(API_KEYS.values())


# 환경 변수 값을 로드하여 변수에 저장
UPSTAGE_API_KEY, LANGCHAIN_API_KEY, TAVILY_API_KEY = load_env()


''' UPSTAGE API 사용 - UpstageEmbeddings '''
# Set up the embedding function
embedding_function = UpstageEmbeddings(model="solar-embedding-1-large")


# 현재 작업 디렉토리를 Github에서 clone한 repository 이름으로 설정
repo_name = "youth_policy"
if not os.getcwd().endswith(repo_name):
    os.chdir(os.path.join(os.getcwd(), repo_name))


persist_directory = "chroma_db"
# Load the vector store from the persist directory
db = Chroma(embedding_function=embedding_function, persist_directory=persist_directory)
retriever = db.as_retriever(search_kwargs={"k": 3})


system_prompt = """
당신은 청년 정책 전문가입니다. 아래 지시 사항을 반드시 지켜서, 청년 정책에 관한 질문에 정확하고 오류 없는 답변을 생성하세요. \

<context 기반 답변 생성 방법>

1. context 기반 답변 : 다음 검색된 context를 기반으로, 질문에 대한 답변을 생성하세요. \
2. context가 없는 경우 : 답변 생성을 위한 context가 없는 경우, "잘 모르겠습니다."라고 답하세요. \
3. 내용의 일관성 유지 : 답변 생성 시, context의 내용을 있는 그대로 서술하고, context에 없는 내용을 절대 생성하지 마세요.\
4. 세부사항 일치 확인 : context의 세부적인 내용과 생성한 답변의 세부적인 내용은 동일해야 합니다. \
5. **금액, 날짜, 숫자 검증 : 특히, 생성한 답변에 금액, 날짜, 숫자가 포함된 경우, context와 동일한지 확인하고, 동일하지 않으면 답변을 삭제하세요.** \
6. 부정확한 내용 삭제 : 생성한 답변에서, **context와 다른 내용은 틀렸으니 삭제하세요.** \
7. 찾은 정책들이 비슷하여 하나로 특정하기 어려운 경우 사용자에게 list를 제공하거나 더 자세한 정보를 요구하세요.\

<질문 유형 기반 답변 생성 방법>

1. 추천 질문 : 정책 추천을 요구하는 질문이라면, 유저의 나이, 거주지, 취업 상태 등을 바탕으로 유저가 지원 가능한 정책을 찾고, 이에 대한 근거를 설명하세요. 이때, 유저의 거주지는 정책을 주관하는 지자체에 포함되어야 합니다. 예를 들어, 유저가 경기도에 거주하는 경우, 충청도가 주관하는 정책을 추천하면 안 되지만, 전국 단위로 주관하는 정책은 추천 가능합니다. \
2. 후기 관련 질문 : “후기”라는 단어가 포함된 질문이라면, 로컬 context가 아닌 tavily의 외부 검색 기능을 활용하세요. \
3. 세부 정보 질문 : 정책의 세부적인 정보를 묻는 질문이라면, 해당 정책명이 정확하게 포함된 context만을 검색해 답변을 생성하세요. \

<기타> 

1. 간결하고 이해하기 쉽게 답변하세요. \
2. 질문에 대한 집중 : 물어본 질문에만 답변하세요. \
3. 명확하지 않은 질문은 다시 : 질문을 명확하게 이해하지 못한 경우, “질문을 다시 구체적으로 해주세요”라고 답하세요. \
4. 질문이 여러 개의 정보를 요구하는 경우, 하위 질문으로 나누어 단계별로 생각하고 답변을 생성하세요.\

context: {context}
"""


''' <지시 + context + 대화 기록 + 유저 질문> 템플릿 '''
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),  # 지시 + context
        MessagesPlaceholder(variable_name="chat_history"),  # 대화 기록
        ("human", "{question}"),  # 유저 질문
    ]
)


''' UPSTAGE API 사용 - ChatUpstage '''
llm = ChatUpstage(max_tokens=200, temperature=0.2, top_p=0.1)
chain = prompt | llm | StrOutputParser()


"""
Represents the state of our graph.
Attributes:
    context: retrieved context
    question: question asked by the user
    answer: generated answer to the question
    groundedness: groundedness of the assistant's response
    chat_history: list of chat messages
"""
class RagState(TypedDict):
    context: str
    question: str
    answer: str
    groundedness: str
    chat_history: List[str]


''' prepare RAG pipeline '''

''' 검색된 문서들의 내용을 하나의 문자열로 포맷 '''
def format_documents(docs: List[Document]) -> str:
    return "\n".join([doc.page_content for doc in docs if hasattr(doc, 'page_content')])


''' 검색 함수 '''
def retrieve(state: RagState) -> RagState:
    # retriever에서 질문과 관련된 문서들을 검색
    docs = retriever.invoke(state["question"])
    # 검색된 문서들의 내용을 하나의 문자열로 포맷 > context 생성
    context = format_documents(docs)
    # 생성된 context를 Ragstate의 context 변수에 저장
    return RagState(context = context)


''' 모델 답변 생성 함수 '''
def model_answer(state: RagState) -> RagState:
    # chain 실행 > 모델이 답변을 생성
    response = chain.invoke(state)
    # 생성된 response를 Ragstate의 answer 변수에 저장
    return RagState(answer = response)


''' 외부 검색 함수 '''
def tavily_search(state: RagState) -> RagState:
    tavily = TavilySearchAPIRetriever(k=3, include_raw_content=True, search_depth='advanced')
    print('Seaching using Tavily...')
    docs_external = tavily.invoke(state["question"])
    # tavily 검색 결과가 있으면
    if docs_external:
        context_tavily = format_documents(docs_external)
        # 외부 검색된 context를 Ragstate의 context 변수에 저장
        return RagState(context = context_tavily)
    else:
        print('No results found from Tavily.')
        return RagState(context = "검색 결과가 없습니다.")


''' UPSTAGE API 사용 - GroundednessCheck '''
gc = GroundednessCheck()
''' context와 answer를 비교하여 답변의 근거성 평가 '''
def groundedness_check(state: RagState) -> RagState:
    response = gc.run({"context": state["context"], "answer": state["answer"]})
    # 생성된 response를 Ragstate의 groundedness 변수에 저장
    return RagState(groundedness = response)


''' RagState의 groundedness 변수 값 출력 '''
def groundedness_condition(state: RagState) -> RagState:
    return state["groundedness"]


''' Build Langgraph '''

workflow = StateGraph(RagState)
workflow.add_node("retrieve", retrieve)  
workflow.add_node("retrieve_again", retrieve) 

workflow.add_node("model", model_answer)  
workflow.add_node("model_again", model_answer)
workflow.add_node("model_tavily", model_answer)

workflow.add_node("groundedness_check_1", groundedness_check) 
workflow.add_node("groundedness_check_2", groundedness_check) 

workflow.add_node("tavily_search", tavily_search)  


# 상태간의 전이를 정의
workflow.add_edge("retrieve", "model")
workflow.add_edge("model", "groundedness_check_1")

workflow.add_edge("retrieve_again", "model_again")
workflow.add_edge("model_again", "groundedness_check_2")


# 근거성 평가 결과에 따라 다른 경로로 전이
workflow.add_conditional_edges(
    "groundedness_check_1",
    groundedness_condition,
    {
        "grounded": END,  # 근거 있음 > workflow 종료
        "notGrounded": "retrieve_again",  # 근거 부족 > 다시 retrieve 단계로 전이
        "notSure": "retrieve_again",  # 불확실 > 다시 retrieve 단계로 전이
    },
)

# 두 번째 근거성 평가 결과에 따라 다른 경로로 전이
workflow.add_conditional_edges(
    "groundedness_check_2",
    groundedness_condition,
    {
        "grounded": END,  # 근거 있음 > workflow 종료
        "notGrounded": "tavily_search",  # 두 번째도 근거 부족 > tavily_search 단계로 전이
        "notSure": "tavily_search",  # 두 번째도 불확실 > tavily_search 단계로 전이
    },
)

# tavily_search 후에는 다시 모델로 이동
workflow.add_edge("tavily_search", "model_tavily")
workflow.add_edge("model_tavily", "groundedness_check_2")

# workflow 시작 지점을 검색 단계로 설정
workflow.set_entry_point("retrieve")

# 정의된 workflow를 compile하여 실행 가능한 상태로 만든다
app = workflow.compile()


chat_history = []

''' Gradio에서 처리될 대화 함수 '''
def chat(question, context):
    global chat_history

    inputs = {
        "question": question,
        "chat_history": chat_history,
        "context": context
    }

    keys = []
    values = []

    answer = ""
    for output in app.stream(inputs):
        for key, value in output.items():
            keys.append(key)
            values.append(value)
    
    answer = values[-2]['answer']  # 최종 gc 결과가 grounded가 나오기 직전의 답변을 저장

    # 대화 기록 업데이트
    chat_history += [str(HumanMessage(inputs["question"])), AIMessage(answer)]

    # Gradio에서 UI로 반환할 값
    return f"{answer}"


with gr.Blocks(css="""

    .gradio-container {
        background-color: #E0FFFF; /* 배경을 연한 하늘색으로 설정 */
        font-family: 'Arial', sans-serif;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1); /* 약간의 그림자 추가 */
        max-width: 800px; /* 전체 컨테이너의 최대 가로 폭 설정 */
        margin: 0 auto; /* 중앙 정렬 */
    }
    h1 {
        font-size: 24px;
        font-weight: bold;
        color: #8A2BE2; 
    }
    .description {
        font-size: 16px;
        color: black;
    }
    .gradio-button {
        background-color: #3498db;
        color: #fff;
        border-radius: 10px;
    }
""") as demo:

    with gr.Column():
        gr.Markdown("<h1 style='text-align: center;'>청년 정책 추천 챗봇</h1>")
        gr.Markdown("<p class='description' style='text-align: center;'>당신께 꼭 필요한 청년 정책을 추천해드릴게요!</p>")

        chatbot = gr.ChatInterface(
            fn = chat,
            chatbot=gr.Chatbot(height=1000),
            textbox=gr.Textbox(placeholder="질문을 입력해 주세요.", container=False, scale=7),
            examples=[
                    ["저는 경기도에 거주하는 23살 대학생입니다. 저에게 맞는 정책을 추천해주세요!"],
                    ["인천 청년월세 지원사업의 신청 기간은 언제인가요?"]
            ],
            retry_btn="다시 보내기",
            undo_btn="이전챗 삭제",
            clear_btn="모두 삭제",
        )
# Gradio 실행
demo.launch(debug=True, share=True)