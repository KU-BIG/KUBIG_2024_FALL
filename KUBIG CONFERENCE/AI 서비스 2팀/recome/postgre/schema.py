from sqlalchemy import Column, Integer, String, Float, Date, Text
from pgvector.sqlalchemy import Vector
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# 테이블 정의
class BookInfo(Base):
    __tablename__ = 'bookinfo'
    id = Column(Integer, primary_key=True, autoincrement=True)  # 기본 키
    category = Column(String(255), nullable=True)  # 카테고리
    subcategory = Column(String(255), nullable=True)  # 분류
    title = Column(String(255), nullable=False)  # 제목
    author = Column(String(255), nullable=True)  # 저자
    publisher = Column(String(255), nullable=True)  # 출판사
    publication_date = Column(Date, nullable=True)  # 출판년월
    review = Column(Integer, nullable=True)  # 리뷰수
    rating = Column(Float, nullable=True)  # 별점
    description = Column(Text, nullable=True)  # 소개
    hashtags = Column(Text, nullable=True)  # 해시태그
    embedding = Column(Vector(512), nullable=False)  # 크기 512의 벡터

class BookInfo1222(Base):
    __tablename__ = 'bookinfo1222'
    id = Column(Integer, primary_key=True, autoincrement=True)  # 기본 키
    category = Column(String(255), nullable=True)  # 카테고리
    subcategory  = Column(String(255), nullable=True)  # 분류
    title  = Column(String(255), nullable=False)  # 제목
    author = Column(String(255), nullable=True)  # 저자
    publisher = Column(String(255), nullable=True)  # 출판사
    publication_date = Column(Date, nullable=True)  # 출판년월
    review = Column(Integer, nullable=True)  # 리뷰수
    rating = Column(Float, nullable=True)  # 별점
    description = Column(Text, nullable=True)  # 소개
    hashtags = Column(Text, nullable=True)  # 해시태그
    embedding = Column(Vector(512), nullable=False)  # 크기 512의 벡터
    imagelink = Column(String(255), nullable=True)  # 크기 512의 벡터

