import os
import httpx
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"


def _enviar(texto: str) -> None:
    if not TOKEN or not CHAT_ID:
        return
    try:
        httpx.post(API_URL, json={"chat_id": CHAT_ID, "text": texto}, timeout=5)
    except Exception:
        pass


def notificar_criacao(tarefa) -> None:
    _enviar(f"[Tarefa criada]: {tarefa.titulo} → [tarefa id]: {tarefa.id}")

def notificar_delecao(tarefa) -> None:
    _enviar(f"[Tarefa deletada]: {tarefa.titulo}")

def notificar_atribuicao(tarefa) -> None:
    _enviar(f"[Tarefa atribuída]: {tarefa.titulo} → [user id]: {tarefa.usuario_id}")


def notificar_conclusao(tarefa) -> None:
    _enviar(f"[Tarefa concluída]: {tarefa.titulo}")
