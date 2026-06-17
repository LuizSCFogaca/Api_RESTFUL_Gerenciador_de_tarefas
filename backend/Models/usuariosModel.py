from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from backend.database import Base
from pydantic import BaseModel
from typing import Optional
from enum import Enum

class Papel(str, Enum):
    usuario = "usuario"
    admin = "admin"

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, nullable=False)
    senha = Column(String, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)  # soft delete: False = conta removida
    # papel define as permissões: "usuario" (padrão) ou "admin"
    papel = Column(String, default="usuario", nullable=False)
    tarefas = relationship("Tarefa", back_populates="dono")

class createUsuario(BaseModel):
    nome: str
    email: str
    senha: str

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    senha: Optional[str] = None
    papel: Optional[Papel] = None  # só admins podem alterar (validado no controller)

class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: str
    papel: str

    class Config:
        from_attributes = True
