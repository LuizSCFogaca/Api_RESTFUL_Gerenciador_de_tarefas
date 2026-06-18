from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
from backend.database import get_db
from backend.Models.tarefaModel import TarefaCreate, TarefaUpdate, TarefaResponse, Prioridade, Status
from backend.Services import tarefaService
from backend.auth import get_current_user, pode_gerenciar

# dependency no router inteiro: todas as rotas de /tasks exigem token JWT válido
router = APIRouter(prefix="/tasks", tags=["Tarefas"], dependencies=[Depends(get_current_user)])

@router.post("", response_model=TarefaResponse, status_code=status.HTTP_201_CREATED)
def criar_tarefa(dados: TarefaCreate, db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    if dados.usuario_id is None:
        dados.usuario_id = usuario.id
    return tarefaService.criar(db, dados)

@router.get("/{tarefa_id}", response_model=TarefaResponse)
def ler_tarefa(tarefa_id: int, db: Session = Depends(get_db)):
    tarefa = tarefaService.buscar_por_id(db, tarefa_id)
    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return tarefa

@router.get("", response_model=list[TarefaResponse])
def listar_tarefas(
    assignedTo: int | None = None,
    status: Status | None = None,
    priority: Prioridade | None = None,
    dueBefore: date | None = None,
    db: Session = Depends(get_db),
):
    # filtro avançado: GET /tasks?assignedTo=&status=&priority=&dueBefore= (todos opcionais)
    return tarefaService.listar(db, assignedTo, status, priority, dueBefore)

@router.put("/{tarefa_id}", response_model=TarefaResponse)
def atualizar_tarefa(tarefa_id: int, dados: TarefaUpdate, db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    tarefa = tarefaService.buscar_por_id(db, tarefa_id)
    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    # só o dono da tarefa ou um admin pode editá-la
    if not pode_gerenciar(usuario, tarefa.usuario_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão para editar esta tarefa")
    return tarefaService.atualizar(db, tarefa, dados)

@router.delete("/{tarefa_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_tarefa(tarefa_id: int, db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    tarefa = tarefaService.buscar_por_id(db, tarefa_id)
    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    # só o dono da tarefa ou um admin pode removê-la (apenas admins deletam tarefas de outros)
    if not pode_gerenciar(usuario, tarefa.usuario_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão para remover esta tarefa")
    tarefaService.remover(db, tarefa)