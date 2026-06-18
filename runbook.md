# Runbook — Gerenciador de Tarefas

Procedimentos operacionais para configurar, executar, testar e operar a API e o bot. Para a visão geral do projeto, veja o [README.md](README.md).

## Pré-requisitos

- **Python 3.12** (imagem base do [Dockerfile](Dockerfile)).
- **Docker** e **Docker Compose** (opcional, para subir tudo de uma vez).
- PostgreSQL apenas se for rodar sem Docker e quiser usar Postgres em vez de SQLite.

## Configuração de ambiente

Copie o exemplo e ajuste os valores:

```bash
cp .env.example .env
```

Variáveis ([.env.example](.env.example)):

| Variável | Função | Padrão / exemplo |
| --- | --- | --- |
| `DATABASE_URL` | Conexão do banco. SQLite para local/testes, PostgreSQL para produção. | `sqlite:///./tasks.db` |
| `SECRET_KEY` | Chave de assinatura dos tokens JWT (HS256). | `sua-chave-secreta-aqui` |
| `TELEGRAM_BOT_TOKEN` | Token do bot usado pela **API** para notificações (opcional). | — |
| `TELEGRAM_CHAT_ID` | Chat de destino das notificações da API (opcional). | — |
| `TELEGRAM_CLIENT_BOT_TOKEN` | Token do **bot cliente** (opcional). | — |
| `API_BASE_URL` | URL da API usada pelo bot cliente. | `http://localhost:8000` |

> Se `TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID` não forem definidos, as notificações são silenciosamente ignoradas (no-op) — a API funciona normalmente.

## Rodar local (sem Docker)

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

- API: `http://localhost:8000`
- Swagger/OpenAPI: `http://localhost:8000/docs`
- Healthcheck simples: `GET /` → `{"Status": "Running"}`

As tabelas são criadas automaticamente no startup ([main.py](main.py)), assim como o admin padrão.

## Rodar com Docker

```bash
docker compose up --build
```

Serviços definidos em [docker-compose.yml](docker-compose.yml):

| Serviço | Container | Porta | Observação |
| --- | --- | --- | --- |
| `db` | `tarefas_db` | `5432` | PostgreSQL 15 (`user_tarefas` / `password_tarefas` / `db_tarefas`). |
| `api` | `tarefas_api` | `8000` | Aponta para o banco pelo host `db`. |
| `bot` | `tarefas_bot` | — | Roda `python -m bot.client_bot`, fala com a API pelo host `api`. |
| `pgadmin` | `tarefas_pgadmin` | `8080` | UI do banco — login `admin@admin.com` / `admin`. |

A `api` só sobe após o healthcheck do `db` passar.

## Bot Telegram (cliente)

Interface conversacional sobre a API. Requer `TELEGRAM_CLIENT_BOT_TOKEN` e `API_BASE_URL` no `.env`.

```bash
python -m bot.client_bot
```

No Docker, o serviço `bot` já executa esse comando. Detalhes do fluxo: [bot/README.md](bot/README.md).

## Testes

```bash
pytest
```

- Usa SQLite isolado (`test.db`), recriado a cada teste.
- O `telegramService` é mockado automaticamente (sem envios reais).
- Detalhes da estratégia: [testes/README.md](testes/README.md).

## Operações comuns e troubleshooting

- **Login / token**: `POST /auth/login` retorna `access_token`. Envie-o nas rotas protegidas no header `Authorization: Bearer <token>`. Tokens expiram em 60 minutos.
- **Admin padrão**: criado no startup se não existir (`admin@teste.com` / `123456`). Use-o para operações administrativas (ex.: deletar tarefas de outros usuários).
- **Reset do banco (local SQLite)**: pare a API e apague o arquivo `tasks.db` (ou `test.db` para testes).
- **Reset do banco (Docker)**: `docker compose down -v` remove o volume `postgres_data`.
- **Porta em uso** (`8000`, `5432`, `8080`): finalize o processo conflitante ou ajuste o mapeamento de portas no `docker-compose.yml`.
- **401 nas rotas protegidas**: token ausente, inválido ou expirado — refaça o login.
