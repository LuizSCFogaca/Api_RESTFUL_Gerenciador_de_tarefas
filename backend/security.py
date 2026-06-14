import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

SECRET_KEY = os.getenv("SECRET_KEY", "troque-esta-chave-secreta-em-producao")
ALGORITHM = "HS256"
EXPIRACAO_MINUTOS = 60


def hash_senha(senha: str) -> str:
    """Gera um hash bcrypt (com salt aleatório) a partir da senha em texto puro."""
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()


def verificar_senha(senha: str, senha_hash: str) -> bool:
    """Compara a senha em texto puro com o hash armazenado."""
    return bcrypt.checkpw(senha.encode(), senha_hash.encode())


def criar_token(usuario_id: int) -> str:
    """Cria um JWT assinado contendo o id do usuário (sub) e a expiração (exp)."""
    payload = {
        "sub": str(usuario_id),  # PyJWT exige que 'sub' seja string
        "exp": datetime.now(timezone.utc) + timedelta(minutes=EXPIRACAO_MINUTOS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decodificar_token(token: str) -> dict:
    """Valida a assinatura e a expiração, retornando o payload. Lança jwt.PyJWTError se inválido."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
