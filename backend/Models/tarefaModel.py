from sqlalchemy import Column, Integer, String, ForeignKey
from backend.database import Base
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import relationship

class Tarefa(Base):
    __tablename__ = "tarefas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String)
    descricao = Column(String)
    status = Column(String, default="pendente")
    # usuario_id é a ÚNICA referência ao dono/responsável da tarefa (FK -> usuarios.id)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    dono = relationship("Usuario", back_populates="tarefas")

class TarefaCreate(BaseModel):
    titulo: str
    descricao: str
    status: Optional[str] = "pendente"
    usuario_id: Optional[int] = None  # a quem a tarefa é atribuída (opcional na criação)

class TarefaResponse(BaseModel):
    id: int
    titulo: str
    descricao: str
    status: str
    usuario_id: Optional[int]

    class Config:
        from_attributes = True

class TarefaUpdate(BaseModel):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    status: Optional[str] = None
    usuario_id: Optional[int] = None
