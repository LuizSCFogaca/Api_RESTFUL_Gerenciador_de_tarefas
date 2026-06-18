# backend/ — Núcleo da API

Camada que implementa toda a API REST. Segue o padrão **MVC em camadas**, onde cada requisição percorre:

```
Controller (HTTP/validação/permissão) → Service (regra de negócio + DB) → Model (ORM + schema) → Banco
```

Os Controllers nunca acessam o banco diretamente; delegam aos Services. Os Models definem tanto as tabelas (SQLAlchemy) quanto os schemas de entrada/saída (Pydantic).

## Arquivos de infraestrutura (raiz de `backend/`)

| Arquivo | Responsabilidade |
| --- | --- |
| `database.py` | Cria o `engine` SQLAlchemy a partir de `DATABASE_URL`, a fábrica de sessões `SessionLocal`, a `Base` declarativa e a dependency `get_db()` (sessão por requisição). |
| `security.py` | Primitivas de segurança: `hash_senha`/`verificar_senha` (bcrypt) e `criar_token`/`decodificar_token` (JWT, `SECRET_KEY`, algoritmo HS256, expiração de 60 minutos). |
| `auth.py` | Dependencies de autorização do FastAPI: `get_current_user` (valida o JWT e carrega o usuário), `requer_admin` (restringe a admins) e o helper `pode_gerenciar(usuario, dono_id)` (dono do recurso **ou** admin). |
| `__init__.py` | Marca o diretório como pacote Python. |

## Subcamadas

| Pasta | Conteúdo | Documentação |
| --- | --- | --- |
| `Controllers/` | Rotas HTTP (`/auth`, `/users`, `/tasks`). | [Controllers/README.md](Controllers/README.md) |
| `Models/` | Modelos ORM e schemas Pydantic. | [Models/README.md](Models/README.md) |
| `Services/` | Regra de negócio, acesso ao banco e notificações. | [Services/README.md](Services/README.md) |

> O ponto de entrada que monta a aplicação e inclui os routers fica na raiz do projeto: [../main.py](../main.py).
