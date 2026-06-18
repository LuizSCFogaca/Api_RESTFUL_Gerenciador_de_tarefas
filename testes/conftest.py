import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from unittest.mock import patch

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

from main import app
from backend.database import Base, get_db

@pytest.fixture(autouse=True)
def mock_telegram():
    """Substitui o telegramService por um mock em todos os testes para evitar envios reais."""
    with patch("backend.Services.tarefaService.telegramService") as mock:
        yield mock

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    with TestClient(app) as c:
        yield c
        
    Base.metadata.drop_all(bind=engine)
