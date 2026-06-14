import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.Services import usuarioService
from backend.security import decodificar_token

# Esquema que lê o header "Authorization: Bearer <token>".
bearer = HTTPBearer()


def get_current_user(
    credenciais: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
):
    """Valida o token JWT e devolve o usuário autenticado. Use como Depends nas rotas protegidas."""
    token = credenciais.credentials
    erro = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decodificar_token(token)
        usuario_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise erro

    usuario = usuarioService.buscar_por_id(db, usuario_id)
    if not usuario:
        raise erro

    return usuario
