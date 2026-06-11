from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.Models.tarefaModel import TarefaCreate, TarefaUpdate, TarefaResponse
from backend.Services import tarefaService
from backend.auth import get_current_user

# dependency no router inteiro: todas as rotas de /tasks exigem token JWT válido
router = APIRouter(prefix="/tasks", tags=["Tarefas"], dependencies=[Depends(get_current_user)])

@router.post("", response_model=TarefaResponse, status_code=status.HTTP_201_CREATED)
def criar_tarefa(dados: TarefaCreate, db: Session = Depends(get_db)):
    return tarefaService.criar(db, dados)

@router.get("/{tarefa_id}", response_model=TarefaResponse)
def ler_tarefa(tarefa_id: int, db: Session = Depends(get_db)):
    tarefa = tarefaService.buscar_por_id(db, tarefa_id)
    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return tarefa

@router.get("", response_model=list[TarefaResponse])
def listar_tarefas(assignedTo: int, db: Session = Depends(get_db)):
    # atende GET /tasks?assignedTo={userId}
    return tarefaService.listar_por_usuario(db, assignedTo)

@router.put("/{tarefa_id}", response_model=TarefaResponse)
def atualizar_tarefa(tarefa_id: int, dados: TarefaUpdate, db: Session = Depends(get_db)):
    tarefa = tarefaService.buscar_por_id(db, tarefa_id)
    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return tarefaService.atualizar(db, tarefa, dados)

@router.delete("/{tarefa_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_tarefa(tarefa_id: int, db: Session = Depends(get_db)):
    tarefa = tarefaService.buscar_por_id(db, tarefa_id)
    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    tarefaService.remover(db, tarefa)