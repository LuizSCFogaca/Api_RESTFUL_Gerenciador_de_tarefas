# backend/Controllers/ — Camada de rotas

Os Controllers expõem os endpoints HTTP, validam entrada/saída (via schemas Pydantic), aplicam as regras de permissão e delegam a lógica aos Services. Cada arquivo define um `APIRouter` que é incluído em [../../main.py](../../main.py).

## `authController.py` — `/auth`

Schemas internos: `LoginRequest` (email + senha) e `TokenResponse` (`access_token` + `token_type`).

| Método | Rota | Descrição |
| --- | --- | --- |
| `POST` | `/auth/login` | Valida credenciais com `verificar_senha` e retorna um JWT (`criar_token`). Retorna **401** se email/senha inválidos. |
| `POST` | `/auth/logout` | Rota protegida (exige `get_current_user`). Retorna mensagem de sucesso — o token é stateless, então o descarte é responsabilidade do cliente. |

## `tarefaController.py` — `/tasks`

O router inteiro exige JWT válido (`dependencies=[Depends(get_current_user)]`).

| Método | Rota | Descrição |
| --- | --- | --- |
| `POST` | `/tasks` | Cria tarefa. Se `usuario_id` não for informado, assume o usuário autenticado como dono. Retorna **201**. |
| `GET` | `/tasks/{id}` | Retorna a tarefa ou **404**. |
| `GET` | `/tasks` | Lista com filtros opcionais combináveis: `assignedTo`, `status`, `priority`, `dueBefore`. |
| `PUT` | `/tasks/{id}` | Atualiza a tarefa. Exige ser **dono ou admin** (`pode_gerenciar`), senão **403**; **404** se inexistente. |
| `DELETE` | `/tasks/{id}` | Remove a tarefa. Mesma regra dono/admin; retorna **204**. |

## `usuarioController.py` — `/users`

| Método | Rota | Descrição |
| --- | --- | --- |
| `POST` | `/users` | Cadastra usuário (rota pública). Retorna **201**. |
| `GET` | `/users/{id}` | Consulta usuário (exige autenticação). **404** se inexistente. |
| `PUT` | `/users/{id}` | Atualiza. Exige ser **o próprio usuário ou admin**; alterar o **papel** exige ser admin (senão **403**). |
| `DELETE` | `/users/{id}` | Remove (soft delete). Exige ser o próprio usuário ou admin; retorna **204**. |

> Regras de permissão usam os helpers de [../auth.py](../auth.py); a lógica de persistência fica em [../Services/README.md](../Services/README.md).
