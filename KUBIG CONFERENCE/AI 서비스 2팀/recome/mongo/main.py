from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from fastapi.middleware.cors import CORSMiddleware
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi
import requests
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json

# MongoDB 연결 설정
ca = certifi.where()
uri = "mongodb+srv://medicalai20242:Recome@recomeuser1.yf0hk.mongodb.net/?retryWrites=true&w=majority&appName=RecomeUser1"
client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=ca)
db = client["UserDB"]
collection = db["Query"]

# OpenAI 클라이언트 초기화
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
openai_client = OpenAI(api_key=openai_api_key)

# FastAPI 앱 인스턴스 생성
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://www.recome.co.kr", "http://3.24.242.112"],  # 허용할 도메인 추가
    allow_credentials=True,
    allow_methods=["*"],  # 허용할 HTTP 메서드 (GET, POST 등)
    allow_headers=["*"],  # 허용할 HTTP 헤더
)
# 기본 엔드포인트
@app.get("/")
async def read_root():
    return {"message": "FastAPI 서버가 잘 작동하고 있습니다!"}

# JSON 파일을 읽고 MongoDB에 데이터 삽입 또는 업데이트하는 함수
def update_user_data(json_file):
    """
    JSON 파일을 읽어서 MongoDB에 user_id를 기준으로 데이터 삽입 또는 새 필드 추가.
    """
    try:
        # JSON 파일 로드
        # with open(json_file, 'r', encoding='utf-8') as f:
        #     data = json.load(f)
        data = json_file
        # 데이터가 객체 형식인지 확인
        # if not isinstance(data, dict):
        #     print("JSON 파일이 객체 형식이 아닙니다.")
        #     return
        
        

        # JSON에서 user_id, query, indices 가져오기
        # user_id = str(data.get("user_id", ""))
        # query = data.get("query", "")
        # indices = data.get("indices", [])
        user_id = str(data.user_id)
        query = data.query
        indices = data.indices
        print("indices", indices)

        if not user_id:
            print("JSON 파일에 user_id가 없습니다.")
            return

        user_data = collection.find_one({"user id": user_id})

        if user_data:
            existing_fields = [key for key in user_data.keys() if key.startswith("query_") or key.startswith("indices_")]
            max_index = max([int(field.split("_")[1]) for field in existing_fields if "_" in field], default=0)
        else:
            max_index = 0

        new_query_field = f"query_{max_index + 1}"
        new_indices_field = f"indices_{max_index + 1}"

        books = ", ".join(map(str, indices)) if indices else ""  # 비어 있으면 공백

        update_fields = {
            "$set": {
                new_query_field: query,
                new_indices_field: books
            }
        }

        collection.update_one({"user id": user_id}, update_fields, upsert=True)
        print(f"user id '{user_id}' 데이터가 저장되었습니다.")

        user_data = collection.find_one({"user id": user_id})
        recent_data = {}
        if user_data:
            query_fields = sorted(
                [(key, user_data[key]) for key in user_data if key.startswith("query_")],
                key=lambda x: int(x[0].split("_")[1]),
                reverse=True
            )
            indices_fields = sorted(
                [(key, user_data[key]) for key in user_data if key.startswith("indices_")],
                key=lambda x: int(x[0].split("_")[1]),
                reverse=True
            )

            for i, (q, idx) in enumerate(zip(query_fields[:3], indices_fields[:3])):
                recent_data[f"query_{i + 1}"] = q[1]
                recent_data[f"indices_{i + 1}"] = idx[1]

        print("최근 추가된 데이터:", recent_data)
        return recent_data

    except FileNotFoundError:
        print(f"JSON 파일 '{json_file}'을 찾을 수 없습니다.")
    except json.JSONDecodeError:
        print("JSON 파일 형식이 올바르지 않습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")

# 사용자 데이터 모델 정의 (Pydantic을 사용)
class KeywordEmbeddingResponse(BaseModel):
    keywords: list[str]  # keywords는 문자열 목록
    vector: list[float]  # vector는 실수 숫자 목록
    indices: list[str]   # 인덱스 목록

# 키워드 추출 함수
def extract_keywords_from_queries(previous_queries, current_query):
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an AI that helps extract meaningful and concise keywords from user input, focusing on specific adjectives, nouns, or descriptive words. "
                    "The goal is to provide a list of individual keywords or phrases that describe the key aspects of the user's input."
                    "Do not include generic terms like '책', '추천', '분위기', '느낌' or any other overly broad or common words. "
                    "Focus on extracting unique, descriptive, and specific adjectives or attributes that reflect the mood, characteristics, or themes of the request."
                )
            },
            {
                "role": "user",
                "content": (
                    f"The user has asked the following questions in the past: {', '.join(previous_queries)}.\n"
                    f"The user is now asking: '{current_query}'.\n"
                    "Please determine if the current query is a completely different question from the previous ones. "
                    "If it is, only extract keywords from the current query. If it is similar to the previous queries, "
                    "combine the previous queries and current query, summarize them, and then extract keywords.\n"
                    "Output the extracted keywords as individual words or short phrases. Please avoid phrases or sentences, and instead output keywords like 'adjectives', 'descriptive words', or 'attributes'."
                    "Do not include words like '책', '추천', '분위기', '느낌' or other general terms, only include more specific descriptive keywords."
                    "Output the extracted keywords only as a comma-separated list. Do not include any other text, explanations, or labels like 'Keywords:'."
                )
            }
        ]
    )
    
    raw_keywords = response.choices[0].message.content.strip().splitlines()  # type: ignore
    keywords = [phrase.strip() for phrase in raw_keywords if phrase.strip()]
    return keywords

# 벡터 임베딩 함수
def generate_embedding(keywords):
    combined_keywords = ", ".join(keywords)

    embs = openai_client.embeddings.create(
        model="text-embedding-3-large",
        input=[combined_keywords],
        encoding_format="float",
        dimensions=512
    )
    
    embedding = embs.data[0].embedding
    return embedding

class JsonFormat(BaseModel):
    indices: list
    query: str
    user_id: str

# API 엔드포인트: 키워드와 임베딩 생성
@app.post("/user")
async def get_keywords_and_embedding(json_file: JsonFormat):

    # MongoDB에서 최근 쿼리와 인덱스 가져오기
    recent_data = update_user_data(json_file)
    if not recent_data:
        return {"error": "No recent data found for the user."}

    queries = [
        recent_data.get("query_1", ""),
        recent_data.get("query_2", ""),
        recent_data.get("query_3", ""),
    ]
    
    indices = [
        recent_data.get("indices_1", ""),
        recent_data.get("indices_2", ""),
        recent_data.get("indices_3", ""),
    ]

    current_query = queries[0]
    previous_queries = [q for q in queries[1:] if q]

    # 키워드 추출
    keywords = extract_keywords_from_queries(previous_queries, current_query)

    # 임베딩 생성
    embedding = generate_embedding(keywords)
    new_query = KeywordEmbeddingResponse(keywords=keywords, vector=embedding, indices=indices)
    new_query_dict = {"keywords": new_query.keywords, "vector": new_query.vector, "indices": new_query.indices}
    output = reranking(new_query_dict)

    return output

# API URL for vector-based search
VECTOR_SEARCH_URL = "http://3.24.242.112:82/books/vector/"
# API URL for fetching book embeddings
SEARCH_URL = "http://3.24.242.112:82/books/search/"

def fetch_top_10_book_ids(query):

    vector_query = {
    "vector": query["vector"],
    "top_n": 10
    }  

    response = requests.post(VECTOR_SEARCH_URL, json=vector_query)
    print(response.status_code)
    if response.status_code == 200:
        books = response.json()  # API 결과를 JSON으로 변환
        # "id"만 추출하여 리스트 생성
        # print(books)
        top_10_ids = [book["id"] for book in books if "id" in book]
        # print(top_10_ids)
        print(f"추출된 상위 10개 책 ID: {top_10_ids}")
        return top_10_ids
    else:
        print(f"검색 실패. 상태 코드: {response.status_code}")
        if "detail" in response.json():
            print("오류 메시지:", response.json()["detail"])
        return []

def reranking(query):
    """
    Rerank the top 10 books based on cosine similarity to the past_list.
    If past_list is not provided, extract top 5 books directly from top_10_list.
    """
    def fetch_book_embedding(book_id):
        response = requests.get(SEARCH_URL, params={"column": "id", "value": str(book_id)})
        if response.status_code == 200:
            book_data = response.json()
            if book_data and "embedding" in book_data[0]:
                return book_data[0], np.array(book_data[0]["embedding"])
        return None, None

    # Extract past_list from indices
    past_list = query["indices"]

    # Fetch top_10_list using vector search
    top_10_list = fetch_top_10_book_ids(query)
    print("top_10_list", top_10_list)
    
    print("past_list", past_list, type(past_list))

    # If past_list is empty, select top 5 directly from top_10_list
    if all(not item for item in past_list):
        print("past_list is empty. Extracting top 5 directly from top_10_list.")
        top_5_books = []
        for book_id in top_10_list[:5]:
            book_data, _ = fetch_book_embedding(book_id)
            if book_data:
                top_5_books.append(book_data)

        # Clean and save the top 5 books
        cleaned_books = []
        for book in top_5_books:
            cleaned_book = {key: value for key, value in book.items() if key not in ["embedding"]}
            cleaned_books.append(cleaned_book)

        # Save cleaned books to a JSON file
        # with open(output_file, "w", encoding="utf-8") as file:
        #     json.dump(cleaned_books, file, ensure_ascii=False, indent=4)

        # print(f"Top 5 books saved to {output_file}")
        print("cleaned_books", len(cleaned_books))
        print("top_5_books", len(top_5_books))
        return cleaned_books

    # Fetch embeddings for past_list books
    past_embeddings = []
    for book_id in past_list:
        _, embedding = fetch_book_embedding(book_id)
        if embedding is not None:
            past_embeddings.append(embedding)
    
    if not past_embeddings:
        print("No embeddings found for past_list books.")
        return

    # Calculate the mean embedding of past_list
    mean_past_embedding = np.mean(past_embeddings, axis=0)

    # Fetch embeddings for top_10_list books and calculate cosine similarity
    ranked_books = []
    for book_id in top_10_list:
        book_data, embedding = fetch_book_embedding(book_id)
        if embedding is not None:
            similarity = cosine_similarity([mean_past_embedding], [embedding])[0][0]
            ranked_books.append((similarity, book_data))

    # Sort books by similarity in descending order
    ranked_books.sort(reverse=True, key=lambda x: x[0])

    # Select the top 5 books
    top_5_books = [book[1] for book in ranked_books[:5]]

    # Remove 'id' and 'embedding' from book data
    cleaned_books = []
    for book in top_5_books:
        cleaned_book = {key: value for key, value in book.items() if key not in ["embedding"]}
        cleaned_books.append(cleaned_book)

    return cleaned_books
    # Save cleaned books to a JSON file
    #with open(output_file, "w", encoding="utf-8") as file:
        #json.dump(cleaned_books, file, ensure_ascii=False, indent=4)