# Gerenciador de Tarefas — API RESTful

API REST para **gestão de tarefas colaborativas**: usuários se cadastram, autenticam-se via JWT, e criam/editam/atribuem/concluem tarefas. Há controle de papéis (`usuario`/`admin`), notificações opcionais via Telegram e um **bot Telegram cliente** que opera como interface conversacional sobre a API.

## Stack

FastAPI · SQLAlchemy · PostgreSQL (SQLite em local/testes) · PyJWT · bcrypt · pytest. Versões fixadas em [requirements.txt](requirements.txt).

## Arquitetura em camadas (MVC)

```
Cliente HTTP / Bot Telegram
        │  (HTTP + JWT Bearer)
        ▼
  Controllers   →  rotas, validação de entrada/saída, permissões
        │
        ▼
   Services      →  regra de negócio, acesso ao banco, notificações
        │
        ▼
    Models       →  ORM SQLAlchemy + schemas Pydantic
        │
        ▼
   Banco (PostgreSQL/SQLite)
```

- O **bot** (`bot/`) é um cliente externo: fala só com a API por HTTP, nunca acessa o banco.
- O **Telegram** (lado API) é usado apenas para notificações de eventos de tarefas.

## Estrutura do projeto

| Pasta | Descrição | Documentação |
| --- | --- | --- |
| `backend/` | Núcleo da API: controllers, services, models e infraestrutura (DB, auth, segurança). | [backend/README.md](backend/README.md) |
| `bot/` | Bot Telegram cliente que consome a API via HTTP. | [bot/README.md](bot/README.md) |
| `testes/` | Suíte de testes automatizados (pytest + TestClient). | [testes/README.md](testes/README.md) |

Arquivos na raiz: [main.py](main.py) (ponto de entrada — registra os routers e cria as tabelas), [Dockerfile](Dockerfile), [docker-compose.yml](docker-compose.yml), [.env.example](.env.example).

Glossário do domínio (Linguagem Ubíqua / DDD): [DICIONARIO.md](DICIONARIO.md).

## Como rodar (resumo)

```bash
cp .env.example .env
pip install -r requirements.txt
uvicorn main:app --reload
```

API em `http://localhost:8000` · documentação Swagger interativa em `http://localhost:8000/docs`.

Passos detalhados (Docker, bot, variáveis de ambiente, troubleshooting): veja o **[runbook.md](runbook.md)**.

## Endpoints (visão geral)

| Método | Rota | Descrição |
| --- | --- | --- |
| `POST` | `/auth/login` | Autentica e retorna um token JWT. |
| `POST` | `/auth/logout` | Logout (rota protegida). |
| `POST` | `/users` | Cadastra usuário. |
| `GET` | `/users/{id}` | Consulta usuário. |
| `PUT` | `/users/{id}` | Atualiza usuário (papel só por admin). |
| `DELETE` | `/users/{id}` | Remove usuário (soft delete). |
| `POST` | `/tasks` | Cria tarefa. |
| `GET` | `/tasks/{id}` | Consulta tarefa. |
| `GET` | `/tasks` | Lista com filtros `assignedTo`, `status`, `priority`, `dueBefore`. |
| `PUT` | `/tasks/{id}` | Atualiza tarefa (dono ou admin). |
| `DELETE` | `/tasks/{id}` | Remove tarefa (dono ou admin). |

Detalhes de cada rota: [backend/Controllers/README.md](backend/Controllers/README.md).

## Admin padrão

No startup da API, um administrador fixo é criado se ainda não existir: **`admin@teste.com`** / **`123456`**. Troque-o em ambientes reais.
