from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from backend.database import Base
from pydantic import BaseModel

class usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, nullable=False)
    senha = Column(String, nullable=False)
    tarefa = relationship("Tarefa", back_populates="dono")

class createUsuario(BaseModel):
    nome: str
    email:str
    senha:str

class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: str

    class Config:
        from_attributes = True