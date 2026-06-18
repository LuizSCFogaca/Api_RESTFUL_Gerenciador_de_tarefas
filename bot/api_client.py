import base64
import json
import os

import httpx
from dotenv import load_dotenv

load_dotenv()

#Dentro do Docker Compose a API responde no host "api"; localmente, em localhost
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


#Faz chamada pra API REST. O bot é um cliente HTTP externo
def chamar_api(metodo: str, caminho: str, jwt: str | None = None, **kwargs) -> httpx.Response:
    headers = kwargs.pop("headers", {})
    if jwt:
        headers["Authorization"] = f"Bearer {jwt}"
    return httpx.request(
        metodo,
        f"{API_BASE_URL}{caminho}",
        headers=headers,
        timeout=15,
        **kwargs,
    )


#Le o 'sub' do payload do JWT sem validar assinatura, só preciso do id
def extrair_user_id(jwt_token: str) -> int | None:
    try:
        payload_b64 = jwt_token.split(".")[1]
        payload_b64 += "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        return int(payload["sub"])
    except Exception:
        return None


#Monta uma mensagem curta preservando o código HTTP devolvido pela API
def detalhe_erro(resp: httpx.Response) -> str:
    try:
        detail = resp.json().get("detail")
    except Exception:
        detail = None

    if isinstance(detail, list) and detail:
        msg = detail[0].get("msg", "dados inválidos")
    elif detail:
        msg = str(detail)
    else:
        msg = resp.reason_phrase or "erro inesperado"
    return f"HTTP {resp.status_code} — {msg}"
