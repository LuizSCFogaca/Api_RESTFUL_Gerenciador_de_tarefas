from fastapi import APIRouter, Depends
from backend.Models.usuariosModel import usuario, UsuarioResponse, createUsuario
from sqlalchemy.orm import Session
from backend.database import get_db
router = APIRouter()

@router.post("usuario", response_model=UsuarioResponse)
def cadastrar_usuario(usuario: createUsuario, db: Session = Depends(get_db)):
    novo_cadastro = usuario(
        nome = usuario.nome,
        email = usuario.email,
        senha = usuario.senha
    )
    db.add(novo_cadastro)
    db.commit()
    db.refresh(novo_cadastro)
    return novo_cadastro
