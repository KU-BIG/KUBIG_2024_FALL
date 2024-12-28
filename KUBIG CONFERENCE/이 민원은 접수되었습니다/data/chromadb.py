from IPython import get_ipython
from dotenv import load_dotenv
import json
import os
import pandas as pd
from langchain.docstore.document import Document
from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
)
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore")
from langchain.vectorstores import Chroma
from langchain_upstage import UpstageEmbeddings


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


# Load JSON files
with open(r'C:\Users\wnsgu\Desktop\upstage\cookbook\file\사진\documents.json', 'r', encoding='utf-8') as f1, \
     open(r'C:\Users\wnsgu\Desktop\upstage\cookbook\file\pdf\documents.json', 'r', encoding='utf-8') as f2:
    docs1 = json.load(f1)
    docs2 = json.load(f2)

# Combine JSON documents
combined_docs = docs1 + docs2

# Convert combined docs to Document objects, checking if 'content' exists and renaming it to 'page_content'
documents = []
for doc in combined_docs:
    if 'content' in doc:
        documents.append(Document(page_content=doc['content'], metadata=doc.get('metadata', {})))
    else:
        print(f"문서에 'content'가 없습니다: {doc}")


# HTML 태그를 제거하는 함수
def clean_html(content):
    soup = BeautifulSoup(content, 'html.parser')
    return soup.get_text()


# 텍스트 분할 함수
def chunking(docs):
    # 텍스트 분할기 설정 (chunk 크기를 1000자로 설정하고, 100자의 오버랩을 설정)
    text_splitter = RecursiveCharacterTextSplitter.from_language(
        chunk_size=1000, chunk_overlap=100, language=Language.HTML
    )

    # 문서를 분할
    split_docs = []
    for doc in docs:
        # HTML 태그 제거
        cleaned_content = clean_html(doc.page_content)

        # 텍스트를 분할
        chunks = text_splitter.split_text(cleaned_content)
        split_docs.extend([Document(page_content=chunk, metadata=doc.metadata) for chunk in chunks])

    return split_docs


# Load youth_policies data and df_sorted
youth_policies_df = pd.read_csv(r'C:\Users\wnsgu\Desktop\upstage\youth_policies_new.csv')
df_sorted = pd.read_csv(r'C:\Users\wnsgu\Desktop\upstage\cookbook\Solar-Fullstack-LLM-101\df_sorted.csv')


# Update document content with youth_policies information
for doc in documents:
    title = doc.metadata.get('title')
    if title in youth_policies_df['정책 ID'].values:
        matching_row = youth_policies_df[youth_policies_df['정책 ID'] == title].iloc[0]
    else:
        # If no match, use the first row or another row from youth_policies_df
        matching_row = youth_policies_df.iloc[0]

    # Combine metadata (except title) into page_content
    additional_content = {key: value for key, value in matching_row.to_dict().items() if key != '정책명'}
    updated_content = f"{doc.page_content}\n\nAdditional Information:\n{json.dumps(additional_content, ensure_ascii=False, indent=2)}"
    doc.page_content = updated_content

    # Update metadata to only include 'title' as '정책명'
    doc.metadata = {'title': matching_row['정책명']}


# Convert youth_policies to Document objects
for index, row in youth_policies_df.iterrows():
    documents.append(Document(
        page_content="",  # Do not add CSV content to page_content
        metadata={'title': row['정책명'], **{key: value for key, value in row.to_dict().items() if key != '정책명'}}
    ))


# Convert df_sorted to Document objects
df_sorted_docs = []
for index, row in df_sorted.iterrows():
    df_sorted_docs.append(Document(
        page_content=row['text'],
        metadata={'title': row['title']}
    ))


# Split documents using the chunking function
split_docs = chunking(documents)


# Split df_sorted documents using the chunking function
split_df_sorted_docs = chunking(df_sorted_docs)


# Save combined JSON for documents and youth_policies
with open(r'C:\Users\wnsgu\Desktop\upstage\cookbook\combined_documents.json', 'w', encoding='utf-8') as f:
    json.dump([doc.dict() for doc in split_docs], f, ensure_ascii=False, indent=4)


# Save split df_sorted documents as a separate JSON file
with open(r'C:\Users\wnsgu\Desktop\upstage\cookbook\split_df_sorted.json', 'w', encoding='utf-8') as f:
    json.dump([doc.dict() for doc in split_df_sorted_docs], f, ensure_ascii=False, indent=4)


# Set the maximum batch size
max_batch_size = 5461  # Chroma의 최대 배치 크기
persist_directory = r'C:\Users\wnsgu\Desktop\upstage\cookbook\chroma_db\new2'


''' UPSTAGE API 사용 - UpstageEmbeddings '''
# Set up the embedding function
embedding_function = UpstageEmbeddings(model="solar-embedding-1-large")

# Initialize the vector store with a persist directory
db = Chroma(embedding_function=embedding_function, persist_directory=persist_directory)

# Function to add documents in batches and persist the vector store
def add_documents_in_batches(db, documents, max_batch_size):
    for i in range(0, len(documents), max_batch_size):
        batch = documents[i:i + max_batch_size]
        db.add_documents(batch)
        print(f"Added batch {i // max_batch_size + 1} of {len(documents) // max_batch_size + 1}")
        db.persist()  # Save the current state after each batch

try:
    # Add split documents to the vector store in batches
    add_documents_in_batches(db, split_docs, max_batch_size)

    # Add split df_sorted documents to the vector store in batches
    add_documents_in_batches(db, split_df_sorted_docs, max_batch_size)

    # Create a retriever from the vector store
    retriever = db.as_retriever()

except Exception as e:
    print(f"An error occurred: {e}")