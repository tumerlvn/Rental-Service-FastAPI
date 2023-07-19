from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_first_project.db"
SQLALCHEMY_DATABASE_URL = "mysql://root:12345Tam@localhost:3306/first_project_db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

if not database_exists(SQLALCHEMY_DATABASE_URL):
    create_database(SQLALCHEMY_DATABASE_URL)



SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()