from sqlalchemy.orm import Session
from backend.Models.usuariosModel import Usuario, createUsuario, UsuarioUpdate
from backend.security import hash_senha

def criar(db: Session, dados: createUsuario) -> Usuario:
    novo = Usuario(
        nome=dados.nome,
        email=dados.email,
        senha=hash_senha(dados.senha),  #nao armazena senha em string pura
        papel="usuario",
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

def garantir_admin_padrao(db: Session) -> None:
    """Cria um admin fixo no startup, caso ainda não exista. Idempotente (seguro rodar sempre)."""
    email = "admin@teste.com"
    existe = db.query(Usuario).filter(Usuario.email == email).first()
    if existe:
        return
    admin = Usuario(
        nome="Admin",
        email=email,
        senha=hash_senha("123456"),
        papel="admin",
    )
    db.add(admin)
    db.commit()

def buscar_por_id(db: Session, usuario_id: int) -> Usuario | None:
    return (
        db.query(Usuario)
        .filter(Usuario.id == usuario_id, Usuario.ativo == True)
        .first()
    )

def buscar_por_email(db: Session, email: str) -> Usuario | None:
    # usado no login para localizar a conta ativa pelo email
    return (
        db.query(Usuario)
        .filter(Usuario.email == email, Usuario.ativo == True)
        .first()
    )

def atualizar(db: Session, usuario: Usuario, dados: UsuarioUpdate) -> Usuario:
    campos = dados.model_dump(exclude_unset=True)
    if "senha" in campos:  #rehash da senha
        campos["senha"] = hash_senha(campos["senha"])
    if "papel" in campos and campos["papel"] not in ("usuario", "admin"):
        campos["papel"] = "usuario"
    for campo, valor in campos.items():
        setattr(usuario, campo, valor)
    db.commit()
    db.refresh(usuario)
    return usuario

def remover(db: Session, usuario: Usuario) -> None:
    usuario.ativo = False #softdelete
    db.commit()
