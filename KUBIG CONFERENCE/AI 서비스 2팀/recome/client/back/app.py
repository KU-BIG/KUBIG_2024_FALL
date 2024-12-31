from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.chat_history import BaseChatMessageHistory

# logging 설정 추가
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Load environment variables
load_dotenv()

class InMemoryHistory(BaseChatMessageHistory):
    """Simple in-memory implementation of chat message history."""
    
    def __init__(self) -> None:
        self.messages: List[Any] = []

    def add_message(self, message: Any) -> None:
        """Add a message to the history."""
        self.messages.append(message)

    def clear(self) -> None:
        """Clear the message history."""
        self.messages = []

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 대화 기록을 저장할 세션 저장소
sessions: Dict[str, InMemoryHistory] = {}

# ChatOpenAI 모델 초기화
chat = ChatOpenAI(
    temperature=0.7,
    model_name="gpt-3.5-turbo",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# 프롬프트 템플릿 정의
prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 전문적이고 친절하게 책을 추천해주는 AI 어시스턴트입니다. 사용자의 질문에 명확하고 도움이 되는 답변을 제공해주세요."),
    ("human", "{input}"),
])

# Runnable 체인 생성
chain = prompt | chat

# RunnableWithMessageHistory 설정
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in sessions:
        sessions[session_id] = InMemoryHistory()
    return sessions[session_id]

chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)

class Message(BaseModel):
    content: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    history: List[Dict[str, Any]]

# routering query
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    max_tokens: int

class ChatChoice(BaseModel):
    choices: list[dict]

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(message: Message):
    try:
        # 체인 실행
        response = await chain_with_history.ainvoke(
            {"input": message.content},
            {"configurable": {"session_id": message.session_id}}
        )

        # 대화 기록 가져오기
        history = sessions[message.session_id].messages
        
        # 대화 기록을 딕셔너리 리스트로 변환
        history_list = []
        for msg in history:
            if isinstance(msg, HumanMessage):
                history_list.append({"role": "human", "content": msg.content})
            elif isinstance(msg, AIMessage):
                history_list.append({"role": "ai", "content": msg.content})

        return ChatResponse(
            response=response.content,
            history=history_list
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/router", response_model=ChatChoice)
async def router(query: ChatRequest):
    try:
        print('step1')
        messages = [
            SystemMessage(content=msg.content) if msg.role == "system" else HumanMessage(content=msg.content)
            for msg in query.messages
        ]
        print('step2')
        # chat.generate 호출
        response = await chat.ainvoke(messages)
        
        # 응답 처리
        classification = response.content.strip()
        print("Classification:", classification)
        
        return {
            "choices": [{
                "message": {
                    "content": classification
                }
            }]
        }
    except Exception as e:
        logger.error("Error in router:", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

'''
@app.post("/user", response_model=ChatResponse)
async def user_endpoint(message: Message):  
'''

@app.get("/history/{session_id}")
async def get_history(session_id: str):
    if session_id not in sessions:
        return {"history": []}
    
    history = sessions[session_id].messages
    history_list = []
    for msg in history:
        if isinstance(msg, HumanMessage):
            history_list.append({"role": "human", "content": msg.content})
        elif isinstance(msg, AIMessage):
            history_list.append({"role": "ai", "content": msg.content})
    
    return {"history": history_list}

@app.delete("/history/{session_id}")
async def clear_history(session_id: str):
    if session_id in sessions:
        sessions[session_id].clear()
    return {"message": "History cleared"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)