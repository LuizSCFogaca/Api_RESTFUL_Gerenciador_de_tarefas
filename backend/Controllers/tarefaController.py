from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.Models.tarefaModel import Tarefa, TarefaCreate, TarefaResponse

router = APIRouter()

@router.post("/tarefas", response_model=TarefaResponse)
def criar_tarefa(tarefa: TarefaCreate, db: Session = Depends(get_db)):
    """
    Cria uma nova tarefa no banco de dados PostgreSQL.
    """
    # 1. Criamos a instância do modelo do banco de dados com os dados recebidos da API
    nova_tarefa = Tarefa(
        titulo=tarefa.titulo,
        descricao=tarefa.descricao,
        status=tarefa.status
    )
    
    # 2. Adicionamos ao banco e confirmamos a transação (commit)
    db.add(nova_tarefa)
    db.commit()
    
    # 3. Atualizamos o objeto 'nova_tarefa' para carregar o ID gerado pelo Postgres
    db.refresh(nova_tarefa)
    
    return nova_tarefa

@router.get("/tarefas/{tarefa_id}", response_model=TarefaResponse)
def ler_tarefa(tarefa_id: int, db: Session = Depends(get_db)):
    """
    Busca uma tarefa específica pelo ID.
    """
    tarefa = db.query(Tarefa).filter(Tarefa.id == tarefa_id).first()
    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return tarefa
