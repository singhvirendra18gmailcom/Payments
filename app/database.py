from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import DATABASE_URL
from pathlib import Path


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
print("FastAPI working directory:", Path.cwd())
print("FastAPI database URL:", DATABASE_URL)
database_path = DATABASE_URL.replace("sqlite:///", "")
print("FastAPI database path:", Path(database_path).resolve())

Base = declarative_base()