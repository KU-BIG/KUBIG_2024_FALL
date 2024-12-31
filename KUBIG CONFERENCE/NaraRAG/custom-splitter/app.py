import os
import uuid
from dotenv import load_dotenv
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- [중요] langchain/Upstage/chroma 관련 임포트들 ---
from langchain_upstage import UpstageEmbeddings, ChatUpstage
from langchain_chroma import Chroma

# parent fs(파일스토어) + docstore
from langchain.storage.file_system import LocalFileStore
from langchain.storage._lc_store import create_kv_docstore

# parent 문서와 연결시키는 Retriever
from langchain.retrievers import ParentDocumentRetriever

# 질문 재구성, 멀티쿼리, RAG 체인 관련
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 환경 변수 로드
load_dotenv()

# FastAPI 초기화
app = FastAPI()

# CORS 설정 (프론트엔드 도메인 등에 맞춰 필요 시 수정)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터 클래스 정의
class ChatRequest(BaseModel):
    input: str
    chat_history: List[Dict[str, str]]  # {"role": "user" | "assistant", "content": str}

class ChatResponse(BaseModel):
    answer: str
    context: str

# ----------------------------------------------------------------------------
# 1) ChromaDB + parent fs 설정
# ----------------------------------------------------------------------------
# 1-1) ChromaDB 로드
vectorstore = Chroma(
    collection_name="split_parents",
    embedding_function=UpstageEmbeddings(model="embedding-passage"),
    persist_directory="child_DB(Chroma, Upstage, Custom2)",
)

# 1-2) 부모 문서(fs)와 연결
fs = LocalFileStore("./parent_fs_chroma_Upstage_Custom2")
store = create_kv_docstore(fs)

# 1-3) 자식 텍스트 쪼개기(Child Splitter)
child_splitter = RecursiveCharacterTextSplitter(chunk_size=400)

# 1-4) ParentDocumentRetriever 생성
parent_retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=store,
    child_splitter=child_splitter,
    search_kwargs={"k": 5}
)

# ----------------------------------------------------------------------------
# 2) 멀티쿼리 + 히스토리(질문 재구성) + RAG 체인 구성
# ----------------------------------------------------------------------------
chat = ChatUpstage()

# MultiQueryRetriever (parent_retriever 사용)
retriever = MultiQueryRetriever.from_llm(
    retriever=parent_retriever,
    llm=chat
)

# 질문 재구성(System 프롬프트)
contextualize_q_system_prompt = """When there are older conversations and more recent user questions, these questions may be related to previous conversations. In this case, change the question to a question that can be understood independently without needing to know the content of the conversation. You don't have to answer the question, just reformulate it if necessary or leave it as is."""

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

# 이전 대화 포함 Retriever
history_aware_retriever = create_history_aware_retriever(
    llm=chat,
    retriever=retriever,
    prompt=contextualize_q_prompt
)

# QA System 프롬프트
qa_system_prompt = """
You are an intelligent assistant helping the members of the Korean National Assembly with questions related to law and policy. Read the given questions carefully and WRITE YOUR ANSWER ONLY BASED ON THE CONTEXT AND DON'T SEARCH ON THE INTERNET. Give the answer in Korean ONLY using the following pieces of the context. You must answer politely.

DO NOT TRY TO MAKE UP AN ANSWER:
 - If the answer to the question cannot be determined from the context alone, say "I cannot determine the answer to that.".
 - If the context is empty, just say "I do not know the answer to that.".

Context: {context}
"""

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        (
            "human",
            "{input}" + " 답변은 구체적으로 최신 정보부터 시간의 흐름에 따라 작성해줘. 그리고 답변할 때 metadata에 있는 source 링크를 함께 제공해줘.",
        ),
    ]
)

# 최종 QA 체인
question_answer_chain = create_stuff_documents_chain(chat, qa_prompt)
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

# ----------------------------------------------------------------------------
# 3) FastAPI 엔드포인트
# ----------------------------------------------------------------------------
@app.post("/api/chat/{chatroom_id}/messages", response_model=ChatResponse)
async def chat_endpoint(chatroom_id: str, request: ChatRequest):
    try:
        print(f"Received message for chatroom {chatroom_id}: {request.dict()}")

        # chat_history가 올바른지 확인
        if not isinstance(request.chat_history, list):
            raise HTTPException(status_code=400, detail="chat_history must be a list")

        # RAG 체인 실행
        result = rag_chain.invoke(
            {
                "input": request.input,
                "chat_history": request.chat_history,
            }
        )

        # context(근거) 파싱
        context = result.get("context", "")
        if isinstance(context, list):
            # Document 객체 리스트일 수도 있음 -> 문자열 형태로 합치기
            context = "\n".join(
                [str(doc) if not isinstance(doc, str) else doc for doc in context]
            )
        elif not isinstance(context, str):
            context = str(context)

        print("RAG result:", result)  # 디버깅용 출력

        return ChatResponse(
            answer=result["answer"],
            context=context,
        )

    except Exception as e:
        print(f"Error in /api/chat/{chatroom_id}/messages:", e)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
