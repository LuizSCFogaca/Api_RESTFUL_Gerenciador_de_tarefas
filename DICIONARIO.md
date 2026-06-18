# Dicionário — Linguagem Ubíqua

Glossário da **Linguagem Ubíqua** (Domain-Driven Design) do Gerenciador de Tarefas. Reúne os termos do domínio usados por toda a equipe, ligando cada conceito ao **identificador correspondente no código**, para que conversa, documentação e implementação falem a mesma língua.

> Convenção: a coluna **No código** indica o nome real usado nos modelos, rotas ou funções. Os modelos estão em [backend/Models/README.md](backend/Models/README.md) e as regras em [backend/Services/README.md](backend/Services/README.md).

## Entidades e atores

| Termo | No código | Definição |
| --- | --- | --- |
| **Usuário** | `Usuario` / tabela `usuarios` | Pessoa cadastrada que se autentica e gerencia tarefas. Possui nome, email, senha (armazenada como hash) e um papel. |
| **Administrador (Admin)** | `Papel.admin` | Usuário com papel elevado. Pode gerenciar tarefas e contas de terceiros (ex.: deletar tarefa de outro usuário, alterar papéis). |
| **Admin padrão** | `garantir_admin_padrao` | Administrador fixo criado automaticamente no startup da API se ainda não existir (`admin@teste.com` / `123456`). |
| **Tarefa** | `Tarefa` / tabela `tarefas` | Unidade de trabalho a ser realizada. Tem título, descrição, status, prioridade, data de vencimento e um dono. |
| **Dono / Responsável** | `usuario_id` (FK) · relação `dono` | Usuário a quem a tarefa pertence/está atribuída. É a única referência de responsabilidade da tarefa. |
| **Bot cliente** | `bot/` (`BotHandlers`) | Cliente externo no Telegram que permite operar a API por uma conversa guiada. Não acessa o banco — só os endpoints HTTP. Ver [bot/README.md](bot/README.md). |

## Atributos e estados

| Termo | No código | Definição |
| --- | --- | --- |
| **Papel** | `Papel` (`usuario`, `admin`) | Nível de permissão de um usuário. Define o que ele pode fazer além dos próprios recursos. |
| **Status (da tarefa)** | `Status` (`pendente`, `em_andamento`, `concluida`) | Estágio atual da tarefa em seu ciclo de vida. |
| **Prioridade** | `Prioridade` (`baixa`, `media`, `alta`) | Grau de urgência/importância da tarefa. |
| **Data de vencimento** | `data_vencimento` | Prazo-limite da tarefa. Opcional; usada no filtro `dueBefore`. |
| **Ativo** | `ativo` (boolean) | Indicador de conta viva. `False` representa uma conta removida (ver Soft delete). |
| **Conta ativa** | `ativo == True` | Usuário não removido. Buscas e login só consideram contas ativas. |

## Ações e operações

| Termo | No código | Definição |
| --- | --- | --- |
| **Cadastrar usuário** | `POST /users` · `usuarioService.criar` | Cria uma nova conta com a senha protegida por hash. |
| **Autenticar / Login** | `POST /auth/login` · `criar_token` | Valida credenciais e emite um token JWT. |
| **Logout** | `POST /auth/logout` | Encerra a sessão do lado do cliente; o token é stateless e apenas descartado. |
| **Criar tarefa** | `POST /tasks` · `tarefaService.criar` | Registra uma nova tarefa; se o dono não for informado, assume o usuário autenticado. |
| **Atribuir tarefa** | `usuario_id` em criar/atualizar · `notificar_atribuicao` | Definir ou trocar o dono de uma tarefa. Dispara notificação. |
| **Concluir tarefa** | `status = concluida` · `notificar_conclusao` | Marcar a tarefa como concluída. A transição para `concluida` dispara notificação. |
| **Listar / Filtrar tarefas** | `GET /tasks` · `tarefaService.listar` | Consulta tarefas aplicando filtros opcionais combináveis (filtro avançado). |
| **Remover tarefa** | `DELETE /tasks/{id}` · `tarefaService.remover` | Exclusão definitiva (hard delete) da tarefa. |
| **Remover usuário** | `DELETE /users/{id}` · `usuarioService.remover` | Remoção lógica da conta (ver Soft delete). |

## Regras e conceitos de domínio

| Termo | No código | Definição |
| --- | --- | --- |
| **Soft delete** | `ativo = False` | Remoção lógica: a conta é marcada como inativa em vez de apagada, preservando histórico e integridade referencial. |
| **Pode gerenciar** | `pode_gerenciar(usuario, dono_id)` | Regra de autorização central: uma ação sobre um recurso é permitida se o solicitante é **dono** do recurso **ou** é **admin**. |
| **Filtro avançado** | `assignedTo`, `status`, `priority`, `dueBefore` | Combinação opcional de critérios na listagem de tarefas; cada filtro só entra na consulta quando informado. |
| **Notificação** | `telegramService.notificar_*` | Aviso enviado pela API ao Telegram em eventos de tarefa (criação, atribuição, conclusão, deleção). É opcional e silencioso se não configurado. |

## Termos técnicos de apoio

| Termo | No código | Definição |
| --- | --- | --- |
| **Token JWT** | `criar_token` / `decodificar_token` | Credencial assinada (HS256) que identifica o usuário autenticado; expira em 60 minutos. Enviada no header `Authorization: Bearer`. |
| **Hash de senha** | `hash_senha` / `verificar_senha` | A senha nunca é armazenada em texto puro: guarda-se um hash bcrypt com salt. |
| **Sessão (do bot)** | `BotHandlers.sessoes` | Estado em memória que associa um chat do Telegram ao seu token e id de usuário. |
| **Fluxo (do bot)** | `BotHandlers.fluxos` | Conversa guiada multi-etapa no bot (ex.: criar conta, nova tarefa), com passos sequenciais. |

> Para o detalhamento dos endpoints, ver [backend/Controllers/README.md](backend/Controllers/README.md). Para a visão geral do projeto, ver [README.md](README.md).
