import os
from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import time
import base64
import uuid
import tempfile
from langchain_upstage import UpstageEmbeddings, ChatUpstage
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, SystemMessage

if "id" not in st.session_state:
    st.session_state.id = uuid.uuid4()
    st.session_state.file_cache = {}

session_id = st.session_state.id
client = None

def reset_chat():
    st.session_state.messages = []
    st.session_state.context = None

DB_PATH = './chroma_db'
vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=UpstageEmbeddings(model="solar-embedding-1-large"))
chat = ChatUpstage(upstage_api_key = 'up_0NlJbP7KsNtBpQm2U0S7uCY3RMnFP')

from langchain.retrievers.multi_query import MultiQueryRetriever
retriever = MultiQueryRetriever.from_llm(
    retriever=vectorstore.as_retriever(), llm=chat)


# 1) 챗봇에 '기억'을 입히기 위한 첫번째 단계

# 이전 메시지들과 최신 사용자 질문을 분석해, 문맥에 대한 정보가 없이 혼자서만 봤을 때 이해할 수 있도록 질문을 다시 구성함.
# 즉 새로 들어온 그 질문 자체에만 집중할 수 있도록 다시 재편성 (llm 예전 대화를 기억해서 대화를 재구성)
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

contextualize_q_system_prompt = "When there are older conversations and more recent user questions, these questions may be related to previous conversations. In this case, change the question to a question that can be understood independently without needing to know the content of the conversation. You don't have to answer the question, just reformulate it if necessary or leave it as is."

# MessagePlaceHolder: 'chat_history' 입력 키를 사용하여 이전 메세지 기록들을 프롬프트에 포함시킴. 
# 즉, 프롬프트, 메세지 기록(문맥 정보), 사용자의 질문으로 프롬프트가 구성됨.

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ('system', contextualize_q_system_prompt),
        MessagesPlaceholder('chat_history'),
        ('human', '{input}'),
    ]
)

# 이를 토대로 메세지 기록을 기억하는 retriever를 생성. 
history_aware_retriever = create_history_aware_retriever(
    chat, retriever, contextualize_q_prompt
)

# 2) 체인을 사용하여 문서를 불러올 수 있는 retriever 체인 생성
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

qa_system_prompt = """
You are an intelligent assistant helping the members of the Korean National Assembly with questions related to law and policy. You must answer politely. Read the given questions carefully and give the answer in Korean ONLY using the following pieces of the context. AGAIN, WRITE YOUR ANSWER ONLY BASED ON THE CONTEXT FROM THE DATABASE AND DON'T SEARCH ON THE INTERNET.

DO NOT TRY TO MAKE UP AN ANSWER:
 - If the answer to the question cannot be determined from the context alone, say "I cannot determine the answer to that.".
 - If the context is empty, just say "I do not know the answer to that.".

Context: {context} """

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ('system', qa_system_prompt),
        MessagesPlaceholder('chat_history'),
        ('human','{input}'+' 답변은 구체적으로 최신 정보부터 시간의 흐름에 따라 작성해줘. 그리고 답변할 때 metadata에 있는 source를 함께 제공해줘.'),
    ]
)

question_answer_chain = create_stuff_documents_chain(chat, qa_prompt)

# 결과값은 input, chat_history, context, answer 포함함.
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
# history_aware_retriever 대신 일반 retriever로 다시 시도


# 웹사이트 제목
st.title("국회 회의록 기반 챗봇 서비스 :orange[NaraRAG] 📜⚖️")

if 'messages' not in st.session_state:
        st.session_state['messages'] = [{'role': 'assistant',
                                         'content': '안녕하세요! 국회 회의록에 관해 궁금한 것이 있으면 언제든 물어봐주세요 😊'}]

# 대화 내용을 기록하기 위해 셋업
# Streamlit 특성상 활성화하지 않으면 내용이 다 날아감.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
# 프롬프트 비용이 너무 많이 소요되는 것을 방지하기 위해
MAX_MESSAGES_BEFORE_DELETION = 4

# 웹사이트에서 유저의 인풋을 받고 위에서 만든 AI 에이전트 실행시켜서 답변 받기
if prompt := st.chat_input("Ask a question!"):
    
# 유저가 보낸 질문이면 유저 아이콘과 질문 보여주기
     # 만약 현재 저장된 대화 내용 기록이 4개보다 많으면 자르기
    if len(st.session_state.messages) >= MAX_MESSAGES_BEFORE_DELETION:
        # Remove the first two messages
        del st.session_state.messages[0]
        del st.session_state.messages[0]  
   
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

# AI가 보낸 답변이면 AI 아이콘이랑 LLM 실행시켜서 답변 받고 스트리밍해서 보여주기
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        result = rag_chain.invoke({"input": prompt, "chat_history": st.session_state.messages})

        # 증거자료 보여주기
        with st.expander("Evidence context"):

            st.write( result['context'])

        for chunk in result["answer"].split(" "):
            full_response += chunk + " "
            time.sleep(0.2)
            message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            
    st.session_state.messages.append({"role": "assistant", "content": full_response})

print("_______________________")
print(st.session_state.messages)