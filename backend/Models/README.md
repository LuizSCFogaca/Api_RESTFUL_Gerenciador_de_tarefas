# backend/Models/ — Modelos e schemas

Cada arquivo combina dois papéis: o **modelo ORM** (SQLAlchemy, mapeia a tabela) e os **schemas Pydantic** (validam entrada e serializam saída das rotas). Os schemas de resposta usam `from_attributes = True` para ler direto dos objetos ORM.

## `usuariosModel.py`

- **Enum `Papel`**: `usuario` (padrão) e `admin`.
- **ORM `Usuario`** (tabela `usuarios`): `id`, `nome`, `email`, `senha` (hash), `ativo` (boolean — **soft delete**: `False` = conta removida), `papel`, e o relacionamento `tarefas` (1-N com `Tarefa`).
- **Schemas**:
  - `createUsuario` — entrada de cadastro (`nome`, `email`, `senha`).
  - `UsuarioUpdate` — atualização parcial; inclui `papel` (alteração validada como exclusiva de admin no controller).
  - `UsuarioResponse` — saída (`id`, `nome`, `email`, `papel`); **nunca expõe a senha**.

## `tarefaModel.py`

- **Enums**: `Prioridade` (`baixa`/`media`/`alta`) e `Status` (`pendente`/`em_andamento`/`concluida`).
- **ORM `Tarefa`** (tabela `tarefas`): `id`, `titulo`, `descricao`, `status`, `prioridade`, `data_vencimento`, `usuario_id` (FK → `usuarios.id`, dono/responsável) e o relacionamento `dono` (lado N).
- **Schemas**:
  - `TarefaCreate` — criação (com defaults `pendente`/`media`; `usuario_id` opcional).
  - `TarefaUpdate` — atualização parcial (todos os campos opcionais).
  - `TarefaResponse` — saída completa da tarefa.

## Modelagem de dados

Duas tabelas com relacionamento **1-N**: um `Usuario` possui muitas `Tarefa`s.

```
usuarios                         tarefas
--------                         -------
id (PK)            1 ────── N    id (PK)
nome                             titulo
email                            descricao
senha (hash)                     status
ativo (soft delete)              prioridade
papel                            data_vencimento
                                 usuario_id (FK → usuarios.id)
```

> O acesso e a manipulação desses modelos ficam na camada de serviços: [../Services/README.md](../Services/README.md).
