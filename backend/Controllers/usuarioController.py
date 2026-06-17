from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.Models.usuariosModel import createUsuario, UsuarioUpdate, UsuarioResponse
from backend.Services import usuarioService
from backend.auth import get_current_user, pode_gerenciar

router = APIRouter(prefix="/users", tags=["Usuários"])

@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def cadastrar_usuario(dados: createUsuario, db: Session = Depends(get_db)):
    return usuarioService.criar(db, dados)

@router.get("/{usuario_id}", response_model=UsuarioResponse, dependencies=[Depends(get_current_user)])
def ler_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = usuarioService.buscar_por_id(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario

@router.put("/{usuario_id}", response_model=UsuarioResponse)
def atualizar_usuario(usuario_id: int, dados: UsuarioUpdate, db: Session = Depends(get_db), autor=Depends(get_current_user)):
    usuario = usuarioService.buscar_por_id(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    # só o próprio usuário ou um admin pode editar a conta
    if not pode_gerenciar(autor, usuario.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão para editar este usuário")
    # apenas admins podem alterar o papel de uma conta
    if dados.papel is not None and autor.papel != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas administradores podem alterar o papel")
    return usuarioService.atualizar(db, usuario, dados)

@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_usuario(usuario_id: int, db: Session = Depends(get_db), autor=Depends(get_current_user)):
    usuario = usuarioService.buscar_por_id(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    # só o próprio usuário ou um admin pode remover a conta
    if not pode_gerenciar(autor, usuario.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão para remover este usuário")
    usuarioService.remover(db, usuario)
