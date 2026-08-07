from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def test_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        print("✅ Connected to PostgreSQL")
        print(result.scalar())


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()