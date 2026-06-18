# testes/ — Testes automatizados

Suíte de testes de integração usando **pytest** + **FastAPI `TestClient`**, exercitando os endpoints de ponta a ponta.

## Estratégia

- **Banco isolado**: SQLite em `test.db`, independente do banco de produção. `DATABASE_URL` é forçada para SQLite antes de importar a aplicação.
- **Isolamento por teste**: a fixture `client` recria todas as tabelas (`drop_all` + `create_all`) antes de cada teste e limpa depois — cada teste começa do zero.
- **Telegram mockado**: a fixture `mock_telegram` (autouse) substitui o `telegramService` para evitar envios reais.
- **Override de dependência**: `get_db` é sobrescrito para usar a sessão de teste.

## Arquivos

| Arquivo | Cobertura |
| --- | --- |
| `conftest.py` | Configuração compartilhada: engine/sessão de teste, override de `get_db`, fixtures `client` e `mock_telegram`. |
| `test_main.py` | Healthcheck da raiz (`GET /` → `{"Status": "Running"}`). |
| `test_auth.py` | Login com sucesso, senha inválida (401), logout autenticado e bloqueio de acesso sem token (401). |
| `test_usuario.py` | Criação de usuário (sem vazar senha), atualização e soft delete (login falha após remover). |
| `test_tarefa.py` | CRUD completo de tarefa, regra de permissão dono/admin (403) e filtros por `status`/`priority`. |

## Como rodar

```bash
pytest
```

Detalhes de ambiente e dependências: [../runbook.md](../runbook.md).
