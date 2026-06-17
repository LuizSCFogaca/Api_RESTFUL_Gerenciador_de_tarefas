from sqlalchemy.orm import Session
from backend.Models.tarefaModel import Tarefa, TarefaCreate, TarefaUpdate, Status
from backend.Services import telegramService

def criar(db: Session, dados: TarefaCreate) -> Tarefa:
    nova = Tarefa(
        titulo=dados.titulo,
        descricao=dados.descricao,
        status=dados.status,
        prioridade=dados.prioridade,
        data_vencimento=dados.data_vencimento,
        usuario_id=dados.usuario_id,
    )
    db.add(nova)
    db.commit()
    db.refresh(nova)
    telegramService.notificar_criacao(nova)
    if nova.usuario_id is not None:
        telegramService.notificar_atribuicao(nova)
    return nova

def buscar_por_id(db: Session, tarefa_id: int) -> Tarefa | None:
    return db.query(Tarefa).filter(Tarefa.id == tarefa_id).first()

def listar(db: Session, assigned_to=None, status=None, prioridade=None, due_before=None) -> list[Tarefa]:
    # cada filtro só entra na query quando o parâmetro vem preenchido
    query = db.query(Tarefa)
    if assigned_to is not None:
        query = query.filter(Tarefa.usuario_id == assigned_to)
    if status is not None:
        query = query.filter(Tarefa.status == status)
    if prioridade is not None:
        query = query.filter(Tarefa.prioridade == prioridade)
    if due_before is not None:
        query = query.filter(Tarefa.data_vencimento <= due_before)
    return query.all()

def atualizar(db: Session, tarefa: Tarefa, dados: TarefaUpdate) -> Tarefa:
    usuario_antigo = tarefa.usuario_id
    status_antigo = tarefa.status

    # exclude_unset=True → só pega os campos que o cliente realmente mandou
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(tarefa, campo, valor)
    db.commit()
    db.refresh(tarefa)

    #tarefa atribuida, ou reatribuida
    if tarefa.usuario_id is not None and tarefa.usuario_id != usuario_antigo:
        telegramService.notificar_atribuicao(tarefa)
    # concluida: status virou concluido agora
    if tarefa.status == Status.concluida and status_antigo != Status.concluida:
        telegramService.notificar_conclusao(tarefa)

    return tarefa

def remover(db: Session, tarefa: Tarefa) -> None:
    db.delete(tarefa)
    db.commit()
    telegramService.notificar_delecao(tarefa)