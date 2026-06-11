from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.Models.usuariosModel import createUsuario, UsuarioUpdate, UsuarioResponse
from backend.Services import usuarioService
from backend.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Usuários"])

# Cadastro é público (registro de novos usuários).
@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def cadastrar_usuario(dados: createUsuario, db: Session = Depends(get_db)):
    return usuarioService.criar(db, dados)

# As rotas abaixo exigem token JWT válido.
@router.get("/{usuario_id}", response_model=UsuarioResponse, dependencies=[Depends(get_current_user)])
def ler_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = usuarioService.buscar_por_id(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario

@router.put("/{usuario_id}", response_model=UsuarioResponse, dependencies=[Depends(get_current_user)])
def atualizar_usuario(usuario_id: int, dados: UsuarioUpdate, db: Session = Depends(get_db)):
    usuario = usuarioService.buscar_por_id(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuarioService.atualizar(db, usuario, dados)

@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_user)])
def remover_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = usuarioService.buscar_por_id(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    usuarioService.remover(db, usuario)
