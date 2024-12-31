from schema import BookInfo, BookInfo1222
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from pgvector.sqlalchemy import Vector  # Ensure pgvector is imported
from typing import List
from threading import Lock  # Thread-safe Singleton 구현

class DatabaseManager:
    _instance = None
    _lock = Lock()

    def __new__(cls, db_url: str):
        """
        Implements Singleton pattern to ensure only one instance is created.
        """
        with cls._lock:
            if not cls._instance:
                cls._instance = super(DatabaseManager, cls).__new__(cls)
                cls._instance._initialize(db_url)
        return cls._instance

    def _initialize(self, db_url: str):
        """
        Initializes the database connection and session maker.
        """
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()  # Single session instance
    
    def add_book(self, book_data: dict) -> None:
        """
        Adds a new book to the database.

        Args:
            book_data (dict): Dictionary containing book information.

        Example:
            book_data = {
                "category": "Fiction",
                "subcategory": "Mystery",
                "title": "The Silent Patient",
                "author": "Alex Michaelides",
                "publisher": "Celadon Books",
                "publication_date": "2019-02-05",
                "review": 12345,
                "rating": 4.5,
                "description": "A shocking psychological thriller.",
                "hashtags": "#thriller #mystery",
                "embedding": [0.1, 0.2, ...]  # Length 512
            }
        """
        # ORM 객체 생성
        new_book = BookInfo1222(
            category=book_data.get("category"),
            subcategory=book_data.get("subcategory"),
            title=book_data["title"],  # Required field
            author=book_data.get("author"),
            publisher=book_data.get("publisher"),
            publication_date=book_data.get("publication_date"),  # Should be in ISO 8601 format (YYYY-MM-DD)
            review=book_data.get("review"),
            rating=book_data.get("rating"),
            description=book_data.get("description"),
            hashtags=book_data.get("hashtags"),
            embedding=book_data["embedding"],  # Required field
            imagelink=book_data["imagelink"]
        )

        # DB에 추가
        # self.session.add(new_book)
        # self.session.commit()
        try:
            self.session.add(new_book)  # 데이터 추가
            self.session.commit()      # 커밋
        except Exception as e:         # 오류 발생 시 처리
            self.session.rollback()    # 롤백하여 트랜잭션 정리
            self.session.close()     # 세션 종료
            self.session = self.Session()  # 새 세션 생성
            print(f"Error adding new book: {e}")  # 오류 로그 출력
       


    def find_book(self, column: str, value: str) -> List[dict]:
        """
        Finds books based on a given column and value.

        Args:
            column (str): Column name to search.
            value (str): Value to search for in the column.

        Returns:
            List[dict]: List of dictionaries containing book details.
        """
        # 컬럼별 조건 정의
        filters = []
        if column == "id":
            # ID로 검색 (정확히 일치)
            filters.append(BookInfo1222.id == int(value))
        elif column in ["category", "subcategory", "title", "author", "publisher", "description", "hashtags"]:
            # 포함된 단어 검색 (LIKE 쿼리)
            filters.append(getattr(BookInfo1222, column).ilike(f"%{value}%"))
        elif column == "publication_date":
            # YYYY-MM 포맷 처리 (YYYY-MM-DD로 변환)
            value = f"{value}-01"
            filters.append(getattr(BookInfo1222, column) == value)
        elif column in ["review", "rating"]:
            # 정확히 일치하는 값 검색
            filters.append(getattr(BookInfo1222, column) == float(value))
        else:
            raise ValueError(f"Invalid column name: {column}")

        # 쿼리 실행
        stmt = select(BookInfo1222).where(*filters)
        results = self.session.execute(stmt).scalars().all()

        # 결과를 JSON 형식으로 변환
        books = [
            {
                "id": book.id,  # ID 포함
                "category": book.category,
                "subcategory": book.subcategory,
                "title": book.title,
                "author": book.author,
                "publisher": book.publisher,
                "publication_date": str(book.publication_date) if book.publication_date else None,
                "review": book.review,
                "rating": book.rating,
                "description": book.description,
                "hashtags": book.hashtags,
                "embedding": book.embedding.tolist() if book.embedding is not None else None,
                "imagelink": book.imagelink
            }
            for book in results
        ]

        return books


    def get_books_by_vector(self, vector: List[float], n: int) -> List[dict]:
        """
        Returns the top n books most similar to the given vector as a list of dictionaries,
        including their cosine similarity scores.

        Args:
            vector (List[float]): Query vector for similarity search.
            n (int): Number of results to return.

        Returns:
            List[dict]: List of dictionaries containing book details and similarity scores.
        """
        # Compute cosine similarity and include it in the query
        similarity = BookInfo1222.embedding.cosine_distance(vector).label("cosine_similarity")

        stmt = (
            select(BookInfo1222, similarity)  # Select both the BookInfo1222 object and the similarity score
            .order_by(similarity)  # Sort by cosine similarity
            .limit(n)  # Limit to top n results
        )

        results = self.session.execute(stmt).all()  # Retrieve all results

        books = [
            {
                "id": book.id,
                "category": book.category,
                "subcategory": book.subcategory,
                "title": book.title,
                "author": book.author,
                "publisher": book.publisher,
                "publication_date": str(book.publication_date) if book.publication_date else None,
                "review": book.review,
                "rating": book.rating,
                "description": book.description,
                "hashtags": book.hashtags,
                "embedding": book.embedding.tolist() if book.embedding is not None else None,
                "imagelink": book.imagelink,
                "cosine_similarity": 1 - similarity_value,  # Include the cosine similarity value
            }
            for book, similarity_value in results
        ]

        return books

