from sqlalchemy.orm import Session
from backend.Models.usuariosModel import Usuario, createUsuario, UsuarioUpdate
from backend.security import hash_senha

def criar(db: Session, dados: createUsuario) -> Usuario:
    novo = Usuario(
        nome=dados.nome,
        email=dados.email,
        senha=hash_senha(dados.senha),  # nunca armazenar a senha em texto puro
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

def buscar_por_id(db: Session, usuario_id: int) -> Usuario | None:
    # Só retorna contas ativas; usuários "soft deleted" ficam invisíveis.
    return (
        db.query(Usuario)
        .filter(Usuario.id == usuario_id, Usuario.ativo == True)
        .first()
    )

def buscar_por_email(db: Session, email: str) -> Usuario | None:
    return (
        db.query(Usuario)
        .filter(Usuario.email == email, Usuario.ativo == True)
        .first()
    )

def atualizar(db: Session, usuario: Usuario, dados: UsuarioUpdate) -> Usuario:
    campos = dados.model_dump(exclude_unset=True)
    if "senha" in campos:  # se a senha mudou, guarda o hash, não o texto puro
        campos["senha"] = hash_senha(campos["senha"])
    for campo, valor in campos.items():
        setattr(usuario, campo, valor)
    db.commit()
    db.refresh(usuario)
    return usuario

def remover(db: Session, usuario: Usuario) -> None:
    # Soft delete: não apaga a linha, apenas marca como inativa.
    usuario.ativo = False
    db.commit()
