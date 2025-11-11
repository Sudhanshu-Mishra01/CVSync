# database.py
from sqlmodel import SQLModel, create_engine, Session

# Hardcoded SQLite path (no config needed)
DATABASE_URL = "sqlite:///./recruitment.db"

engine = create_engine(DATABASE_URL, echo=False)

def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    SQLModel.metadata.create_all(engine)
    print("Database initialized at recruitment.db")