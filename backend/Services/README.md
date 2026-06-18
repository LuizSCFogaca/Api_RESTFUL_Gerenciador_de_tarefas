# backend/Services/ — Regra de negócio

Camada que concentra a lógica de negócio e o acesso ao banco. Recebe a sessão (`Session`) e os schemas vindos dos Controllers, manipula os modelos ORM e dispara efeitos colaterais (notificações). Todos os módulos usam `logging` para registrar as operações.

## `usuarioService.py`

| Função | Descrição |
| --- | --- |
| `criar(db, dados)` | Cria usuário com a senha já protegida por `hash_senha`; papel inicial `usuario`. |
| `garantir_admin_padrao(db)` | Cria o admin fixo (`admin@teste.com` / `123456`) no startup se não existir. **Idempotente** — seguro rodar sempre. |
| `buscar_por_id(db, id)` | Busca usuário **ativo** por id. |
| `buscar_por_email(db, email)` | Busca usuário **ativo** por email (usado no login). |
| `atualizar(db, usuario, dados)` | Atualização parcial (`exclude_unset`); refaz o hash se a senha mudar. |
| `remover(db, usuario)` | **Soft delete**: marca `ativo = False` em vez de apagar. |

## `tarefaService.py`

| Função | Descrição |
| --- | --- |
| `criar(db, dados)` | Persiste a tarefa e notifica criação; se houver dono, notifica atribuição. |
| `buscar_por_id(db, id)` | Retorna a tarefa ou `None`. |
| `listar(db, assigned_to, status, prioridade, due_before)` | Monta a query aplicando apenas os filtros preenchidos. |
| `atualizar(db, tarefa, dados)` | Atualização parcial; notifica **atribuição** se o dono mudou e **conclusão** quando o status passa a `concluida`. |
| `remover(db, tarefa)` | Apaga a tarefa (hard delete) e notifica a deleção. |

## `telegramService.py`

Integração de notificações da **API** com o Telegram (distinto do bot cliente em `bot/`).

- `_enviar(texto)` — envia mensagem via API do Telegram. **No-op** se `TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID` não estiverem definidos; falhas de rede são ignoradas para não quebrar a requisição.
- `notificar_criacao` / `notificar_atribuicao` / `notificar_conclusao` / `notificar_delecao` — mensagens formatadas para cada evento de tarefa.

> Os modelos manipulados aqui estão em [../Models/README.md](../Models/README.md); `hash_senha` vem de [../security.py](../security.py).
