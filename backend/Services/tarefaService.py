from sqlalchemy.orm import Session
from backend.Models.tarefaModel import Tarefa, TarefaCreate, TarefaUpdate

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
    return nova

def buscar_por_id(db: Session, tarefa_id: int) -> Tarefa | None:
    return db.query(Tarefa).filter(Tarefa.id == tarefa_id).first()

def listar_por_usuario(db: Session, usuario_id: int) -> list[Tarefa]:
    return db.query(Tarefa).filter(Tarefa.usuario_id == usuario_id).all()

def atualizar(db: Session, tarefa: Tarefa, dados: TarefaUpdate) -> Tarefa:
    # exclude_unset=True → só pega os campos que o cliente realmente mandou
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(tarefa, campo, valor)
    db.commit()
    db.refresh(tarefa)
    return tarefa

def remover(db: Session, tarefa: Tarefa) -> None:
    db.delete(tarefa)
    db.commit()