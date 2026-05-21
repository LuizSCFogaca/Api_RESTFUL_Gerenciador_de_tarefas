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
    atribuida = Column(Integer, nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuario_id"))
    dono = relationship("Usuario", back_populates="tarefas")

class TarefaCreate(BaseModel):
    titulo: str
    descricao: str
    status: Optional[str] = "pendente"

class TarefaResponse(BaseModel):
    id: int
    titulo: str
    descricao: str
    status: str
    atribuida: Optional[int]

    class Config:
        from_attributes = True
