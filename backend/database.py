from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Banco SQLite local (arquivo tarefas.db na raiz do projeto).
SQLALCHEMY_DATABASE_URL = "sqlite:///./tarefas.db"

# check_same_thread=False é necessário para o SQLite funcionar com o FastAPI,
# que pode acessar a conexão em threads diferentes.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
