from sqlalchemy.orm import Session
from backend.Models.tarefaModel import Tarefa, TarefaCreate, TarefaUpdate
from backend.Services import telegramService

# valores de status que contam como "tarefa concluida"
STATUS_CONCLUIDO = {"concluida", "concluído", "concluido", "concluída"}

def criar(db: Session, dados: TarefaCreate) -> Tarefa:
    nova = Tarefa(
        titulo=dados.titulo,
        descricao=dados.descricao,
        status=dados.status,
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

def listar_por_usuario(db: Session, usuario_id: int) -> list[Tarefa]:
    return db.query(Tarefa).filter(Tarefa.usuario_id == usuario_id).all()

def atualizar(db: Session, tarefa: Tarefa, dados: TarefaUpdate) -> Tarefa:
    # guarda os valores antigos para detectar atribuicao/conclusao
    usuario_antigo = tarefa.usuario_id
    status_antigo = tarefa.status

    # exclude_unset=True → só pega os campos que o cliente realmente mandou
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(tarefa, campo, valor)
    db.commit()
    db.refresh(tarefa)

    # atribuida: ganhou (ou trocou de) responsavel
    if tarefa.usuario_id is not None and tarefa.usuario_id != usuario_antigo:
        telegramService.notificar_atribuicao(tarefa)
    # concluida: status virou concluido agora
    if tarefa.status in STATUS_CONCLUIDO and status_antigo not in STATUS_CONCLUIDO:
        telegramService.notificar_conclusao(tarefa)

    return tarefa

def remover(db: Session, tarefa: Tarefa) -> None:
    db.delete(tarefa)
    db.commit()
    telegramService.notificar_delecao(tarefa)