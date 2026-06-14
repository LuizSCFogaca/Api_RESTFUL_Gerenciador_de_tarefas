from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.database import get_db
from backend.Services import usuarioService
from backend.security import verificar_senha, criar_token
from backend.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Autenticação"])


class LoginRequest(BaseModel):
    email: str
    senha: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse)
def login(dados: LoginRequest, db: Session = Depends(get_db)):
    usuario = usuarioService.buscar_por_email(db, dados.email)
    if not usuario or not verificar_senha(dados.senha, usuario.senha):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha inválidos",
        )
    return TokenResponse(access_token=criar_token(usuario.id))


@router.post("/logout")
def logout(usuario=Depends(get_current_user)):
    return {"mensagem": "Logout realizado com sucesso"}
