from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError
from postgre import DatabaseManager

# DatabaseManager import 필요
# from your_module import DatabaseManager, BookInfo

app = FastAPI()

# 데이터베이스 연결 URL
DATABASE_URL = "postgresql+psycopg2://jwj51720:2084@localhost:5432/book"

# Singleton Database Manager
db_manager = DatabaseManager(DATABASE_URL)


# Pydantic 모델 정의
class BookInput(BaseModel):
    category: Optional[str]
    subcategory: Optional[str]
    title: str
    author: Optional[str]
    publisher: Optional[str]
    publication_date: Optional[str]  # YYYY-MM-DD 형식
    review: Optional[int]
    rating: Optional[float]
    description: Optional[str]
    hashtags: Optional[str]
    embedding: List[float]  # 길이 512의 벡터

class BookInput1222(BaseModel):
    category: Optional[str]
    subcategory: Optional[str]
    title: str
    author: Optional[str]
    publisher: Optional[str]
    publication_date: Optional[str]  # YYYY-MM-DD 형식
    review: Optional[int]
    rating: Optional[float]
    description: Optional[str]
    hashtags: Optional[str]
    embedding: List[float]  # 길이 512의 벡터
    imagelink: Optional[str]


class VectorQuery(BaseModel):
    vector: List[float]
    top_n: int = 5


@app.post("/books/")
async def add_book(book: BookInput1222):
    """
    Adds a new book to the database.

    Args:
        book (BookInput): The book information to be added. Must include:
            - category (str, optional): Category of the book.
            - subcategory (str, optional): Subcategory of the book.
            - title (str): Title of the book (required).
            - author (str, optional): Author of the book.
            - publisher (str, optional): Publisher of the book.
            - publication_date (str, optional): Publication date in 'YYYY-MM-DD' format.
            - review (int, optional): Number of reviews.
            - rating (float, optional): Rating of the book.
            - description (str, optional): Description of the book.
            - hashtags (str, optional): Hashtags associated with the book.
            - embedding (List[float]): 512-dimensional vector representing the book (required).
            - imagelink (List[str]): 새로 추가된 이미지 링크크

    Returns:
        dict: A confirmation message if the book is added successfully.

    Raises:
        HTTPException: If a database error occurs.
    """
    try:
        db_manager.add_book(book.dict())
        return {"message": "Book added successfully"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/books/search/")
async def search_books(column: str, value: str):
    """
    Searches for books based on a specific column and value.

    Args:
        column (str): The column to search in. Supported columns:
            - "id" (exact numeric match)
            - "category", "subcategory", "title", "author", "publisher",
              "description", "hashtags" (partial matching).
            - "publication_date" (exact match, expects 'YYYY-MM' and appends '-01').
            - "review", "rating" (exact numeric match).
        value (str): The value to search for in the specified column.

    Returns:
        List[dict]: A list of books matching the criteria, each as a dictionary with:
            - id (int)
            - category (str)
            - subcategory (str)
            - title (str)
            - author (str)
            - publisher (str)
            - publication_date (str)
            - review (int)
            - rating (float)
            - description (str)
            - hashtags (str)
            - imagelink (str)

    Raises:
        HTTPException: If no books are found, an invalid column is specified,
                       or a database error occurs.
    """
    try:
        results = db_manager.find_book(column, value)
        if not results:
            raise HTTPException(status_code=404, detail="No books found")
        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")



@app.post("/books/vector/")
async def get_books_by_vector(query: VectorQuery):
    """
    Searches for books based on vector similarity.

    Args:
        query (VectorQuery): A query object containing:
            - vector (List[float]): A 512-dimensional vector for similarity search.
            - top_n (int): Number of top results to return.

    Returns:
        List[dict]: A list of the most similar books, each as a dictionary with:
            - category (str)
            - subcategory (str)
            - title (str)
            - author (str)
            - publisher (str)
            - publication_date (str)
            - review (int)
            - rating (float)
            - description (str)
            - hashtags (str)
            - imagelink (str)
            - cosine_similarity (float): Cosine similarity score (-1 to 1).

    Raises:
        HTTPException: If the vector length is not 512, no books are found,
                       or a database error occurs.
    """
    if len(query.vector) != 512:
        raise HTTPException(status_code=400, detail="Vector length must be 512")

    try:
        results = db_manager.get_books_by_vector(query.vector, query.top_n)
        if not results:
            raise HTTPException(status_code=404, detail="No books found")
        return results
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
