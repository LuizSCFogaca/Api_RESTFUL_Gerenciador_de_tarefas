# bot/ — Bot Telegram (cliente)

Interface conversacional sobre a API. É um **cliente HTTP externo**: fala exclusivamente com os endpoints REST, **nunca importa o backend nem acessa o banco**. Mantém sessões de usuário em memória (JWT por `chat_id`).

Execução: `python -m bot.client_bot` (requer `TELEGRAM_CLIENT_BOT_TOKEN` e `API_BASE_URL` no `.env`). Veja o [../runbook.md](../runbook.md).

## `client_bot.py` — loop principal

- `buscar_updates(offset)` — long polling em `getUpdates` do Telegram.
- `enviar(chat_id, texto, opcoes)` — envia mensagem; com `opcoes`, monta um teclado de botões.
- `main()` — valida o token e roda o loop infinito, repassando cada update aos handlers.

## `api_client.py` — comunicação com a API

- `chamar_api(metodo, caminho, jwt, **kwargs)` — wrapper HTTP (httpx) que injeta o header `Authorization: Bearer`. `API_BASE_URL` aponta para `localhost` localmente ou para o host `api` no Docker Compose.
- `extrair_user_id(jwt_token)` — lê o claim `sub` do payload do JWT **sem validar a assinatura** (só para obter o id do usuário).
- `detalhe_erro(resp)` — formata uma mensagem curta de erro preservando o status HTTP retornado pela API.

## `handlers.py` — máquina de estados

`BotHandlers` orquestra menus, sessões e fluxos multi-etapa:

- **Sessões** (`sessoes`): `chat_id → {jwt, user_id}`. **Fluxos** (`fluxos`) e **menus** (`menus`) controlam o passo-a-passo de cada conversa.
- **Menus**: `inicial` (Criar conta / Login), `principal` (Tarefas / Conta / Logout), `tarefas` (Listar / Nova / Voltar), `conta` (Meu perfil / Atualizar / Excluir / Voltar).
- **Fluxos guiados**: criar conta, login, nova tarefa (título → descrição → prioridade), editar perfil e excluir conta (com confirmação).
- `tratar(update)` é o ponto de entrada: trata `/start`, comandos de `Voltar`/`Cancelar` e roteia para o menu ou fluxo ativo.

## `__init__.py`

Marca o diretório como pacote Python.

> A API consumida por este bot está documentada em [../backend/Controllers/README.md](../backend/Controllers/README.md).
