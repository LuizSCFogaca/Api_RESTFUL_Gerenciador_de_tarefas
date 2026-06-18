"""
Esse bot funciona como uma interface para o cliente: permite que o usuário interaja com a API através de um menu

CLIENTE da API REST — ele NÃO acessa o banco nem importa o backend
Tudo passa pelos endpoints HTTP
"""
import os
import time

import httpx
from dotenv import load_dotenv

from bot.api_client import API_BASE_URL
from bot.handlers import BotHandlers

load_dotenv()

TOKEN = os.getenv("TELEGRAM_CLIENT_BOT_TOKEN")
TG_URL = f"https://api.telegram.org/bot{TOKEN}"


#Envia uma mensagem, se "opcoes" vier, mostra balões
def enviar(chat_id: int, texto: str, opcoes: list[str] | None = None) -> None:
    payload = {"chat_id": chat_id, "text": texto}
    if opcoes:
        linhas = [opcoes[i:i + 2] for i in range(0, len(opcoes), 2)]
        payload["reply_markup"] = {
            "keyboard": [[{"text": o} for o in linha] for linha in linhas],
            "resize_keyboard": True,
        }
    else:
        payload["reply_markup"] = {"remove_keyboard": True}

    try:
        httpx.post(f"{TG_URL}/sendMessage", json=payload, timeout=10)
    except Exception:
        pass


#bloqueia até chegar mensagem ou estourar o timeout
def buscar_updates(offset: int | None) -> list[dict]:
    params = {"timeout": 30}
    if offset is not None:
        params["offset"] = offset

    try:
        resp = httpx.get(f"{TG_URL}/getUpdates", params=params, timeout=40)
        return resp.json().get("result", [])
    except Exception:
        time.sleep(3)
        return []


handlers = BotHandlers(enviar)


def tratar(update: dict) -> None:
    handlers.tratar(update)


def main() -> None:
    if not TOKEN:
        raise SystemExit("Defina TELEGRAM_CLIENT_BOT_TOKEN no .env")

    print(f"Bot client-side iniciado. API: {API_BASE_URL}")
    offset = None
    while True:
        for update in buscar_updates(offset):
            offset = update["update_id"] + 1
            try:
                tratar(update)
            except Exception as e:
                print(f"erro ao tratar update: {e}")


if __name__ == "__main__":
    main()
