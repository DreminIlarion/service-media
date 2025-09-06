from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import quote_plus
import os

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "Test1")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", ":@XpTZGQq>It,1")
DB_PORT = os.getenv("DB_PORT", "5432")

escaped_password = quote_plus(DB_PASSWORD)

SQLALCHEMY_DATABASE_URL = f'postgresql://{DB_USER}:{escaped_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency для получения синхронной сессии БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()