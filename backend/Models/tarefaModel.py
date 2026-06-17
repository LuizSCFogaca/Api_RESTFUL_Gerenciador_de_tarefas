from sqlalchemy import Column, Integer, String, ForeignKey, Date
from backend.database import Base
from pydantic import BaseModel
from typing import Optional
from datetime import date
from enum import Enum
from sqlalchemy.orm import relationship

class Prioridade(str, Enum):
    baixa = "baixa"
    media = "media"
    alta = "alta"

class Status(str, Enum):
    pendente = "pendente"
    em_andamento = "em_andamento"
    concluida = "concluida"

class Tarefa(Base):
    __tablename__ = "tarefas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String)
    descricao = Column(String)
    status = Column(String, default="pendente")
    prioridade = Column(String, default="media")
    data_vencimento = Column(Date, nullable=True)
    # usuario_id é a ÚNICA referência ao dono/responsável da tarefa (FK -> usuarios.id)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    dono = relationship("Usuario", back_populates="tarefas")

class TarefaCreate(BaseModel):
    titulo: str
    descricao: str
    status: Optional[Status] = Status.pendente
    prioridade: Optional[Prioridade] = Prioridade.media
    data_vencimento: Optional[date] = None
    usuario_id: Optional[int] = None

class TarefaResponse(BaseModel):
    id: int
    titulo: str
    descricao: str
    status: Status
    prioridade: Prioridade
    data_vencimento: Optional[date]
    usuario_id: Optional[int]

    class Config:
        from_attributes = True

class TarefaUpdate(BaseModel):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    status: Optional[Status] = None
    prioridade: Optional[Prioridade] = None
    data_vencimento: Optional[date] = None
    usuario_id: Optional[int] = None
