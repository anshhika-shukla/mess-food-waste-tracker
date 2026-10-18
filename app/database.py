import os
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Database URL: SQLite by default for zero-config immediate execution, with PostgreSQL compatibility
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mess_tracker.db")

# For SQLite, check_same_thread is False to allow FastAPI multi-threaded requests
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

# Crucial for SQLite: Enable strict Foreign Key enforcement & cascades on every connection
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """FastAPI dependency to yield database sessions with auto-closing."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Initializes all database tables adhering to constraints."""
    Base.metadata.create_all(bind=engine)
