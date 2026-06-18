from collections.abc import Callable

from bot.api_client import chamar_api, detalhe_erro, extrair_user_id

PRIORIDADES = ["baixa", "media", "alta"]
CONFIRMACAO = ["Sim, excluir", "Cancelar"]
CAMPO_KEY = {"Nome": "nome", "Email": "email", "Senha": "senha"}

Enviar = Callable[[int, str, list[str] | None], None]


#Controla menus, sessões e fluxos do bot client-side
class BotHandlers:
    def __init__(self, enviar: Enviar):
        self.enviar = enviar
        self.sessoes = {}  #chat_id -> {"jwt": str, "user_id": int}
        self.fluxos = {}   #chat_id -> {"acao": str, "passo": str, "dados": dict}
        self.menus = {}    #chat_id -> estado do menu atual

    def api(self, metodo: str, caminho: str, chat_id: int | None = None, **kwargs):
        jwt = None
        if chat_id is not None and chat_id in self.sessoes:
            jwt = self.sessoes[chat_id]["jwt"]
        return chamar_api(metodo, caminho, jwt=jwt, **kwargs)

    def texto_menu(self, estado: str) -> str:
        if estado == "inicial":
            return "Escolha uma opção:"
        if estado == "principal":
            return "Menu principal:"
        if estado == "tarefas":
            return "Tarefas:"
        if estado == "conta":
            return "Conta:"
        return "Menu:"

    def opcoes_menu(self, estado: str) -> list[str]:
        if estado == "inicial":
            return ["Criar conta", "Login"]
        if estado == "principal":
            return ["Tarefas", "Conta", "Logout"]
        if estado == "tarefas":
            return ["Listar tarefas", "Nova tarefa", "Voltar"]
        if estado == "conta":
            return ["Meu perfil", "Atualizar perfil", "Excluir conta", "Voltar"]
        return []

    def mostrar_menu(self, chat_id: int, estado: str) -> None:
        self.menus[chat_id] = estado
        self.enviar(chat_id, self.texto_menu(estado), self.opcoes_menu(estado))

    def menu_logado(self, chat_id: int) -> str:
        return "principal" if chat_id in self.sessoes else "inicial"

    def cmd_start(self, chat_id: int) -> None:
        self.fluxos.pop(chat_id, None)
        self.mostrar_menu(chat_id, self.menu_logado(chat_id))

    def cmd_logout(self, chat_id: int) -> None:
        self.sessoes.pop(chat_id, None)
        self.fluxos.pop(chat_id, None)
        self.enviar(chat_id, "[Deslogou]", None)
        self.mostrar_menu(chat_id, "inicial")

    def acao_listar_tarefas(self, chat_id: int) -> None:
        user_id = self.sessoes[chat_id]["user_id"]
        resp = self.api("GET", f"/tasks?assignedTo={user_id}", chat_id=chat_id)

        if resp.status_code != 200:
            self.enviar(chat_id, detalhe_erro(resp), None)
        else:
            tarefas = resp.json()
            if not tarefas:
                self.enviar(chat_id, "Você não tem tarefas ainda.", None)
            else:
                linhas = [
                    f"#{t['id']} - {t['titulo']} [{t['status']} | prioridade {t['prioridade']}]"
                    for t in tarefas
                ]
                self.enviar(chat_id, "Tarefas:\n" + "\n".join(linhas), None)
        self.mostrar_menu(chat_id, "tarefas")

    def acao_meu_perfil(self, chat_id: int) -> None:
        user_id = self.sessoes[chat_id]["user_id"]
        resp = self.api("GET", f"/users/{user_id}", chat_id=chat_id)

        if resp.status_code == 200:
            usuario = resp.json()
            self.enviar(chat_id, f"Usuário #{usuario['id']}: {usuario['nome']}\nEmail: {usuario['email']}", None)
        else:
            self.enviar(chat_id, detalhe_erro(resp), None)
        self.mostrar_menu(chat_id, "conta")

    def iniciar_fluxo(self, chat_id: int, acao: str) -> None:
        if acao == "criar":
            self.fluxos[chat_id] = {"acao": "criar", "passo": "nome", "dados": {}}
            self.enviar(chat_id, "Vamos criar sua conta! Qual é o seu nome?", None)
        elif acao == "login":
            self.fluxos[chat_id] = {"acao": "login", "passo": "email", "dados": {}}
            self.enviar(chat_id, "Digite seu email:", None)
        elif acao == "novatarefa":
            self.fluxos[chat_id] = {"acao": "novatarefa", "passo": "titulo", "dados": {}}
            self.enviar(chat_id, "Qual o título da tarefa?", None)
        elif acao == "editar_perfil":
            self.fluxos[chat_id] = {"acao": "editar", "passo": "campo", "dados": {}}
            self.enviar(chat_id, "Qual campo deseja atualizar?", list(CAMPO_KEY) + ["Voltar"])
        elif acao == "excluir_conta":
            self.fluxos[chat_id] = {"acao": "excluir", "passo": "confirmar", "dados": {}}
            self.enviar(chat_id, "Tem certeza que deseja excluir sua conta?", CONFIRMACAO)

    def continuar_fluxo(self, chat_id: int, texto: str) -> None:
        fluxo = self.fluxos[chat_id]
        acao, passo, dados = fluxo["acao"], fluxo["passo"], fluxo["dados"]

        if acao == "criar":
            self.continuar_criacao_conta(chat_id, texto, passo, dados, fluxo)
        elif acao == "login":
            self.continuar_login(chat_id, texto, passo, dados, fluxo)
        elif acao == "novatarefa":
            self.continuar_nova_tarefa(chat_id, texto, passo, dados, fluxo)
        elif acao == "editar":
            self.continuar_edicao_perfil(chat_id, texto, passo, dados, fluxo)
        elif acao == "excluir":
            self.continuar_exclusao_conta(chat_id, texto, passo)

    def continuar_criacao_conta(self, chat_id: int, texto: str, passo: str, dados: dict, fluxo: dict) -> None:
        if passo == "nome":
            dados["nome"] = texto
            fluxo["passo"] = "email"
            self.enviar(chat_id, "Qual o seu email?", None)
        elif passo == "email":
            dados["email"] = texto
            fluxo["passo"] = "senha"
            self.enviar(chat_id, "Escolha uma senha:", None)
        elif passo == "senha":
            dados["senha"] = texto
            resp = self.api("POST", "/users", json=dados)
            self.fluxos.pop(chat_id, None)
            if resp.status_code == 201:
                self.enviar(chat_id, "Conta criada. Agora faça login.", None)
            else:
                self.enviar(chat_id, detalhe_erro(resp), None)
            self.mostrar_menu(chat_id, "inicial")

    def continuar_login(self, chat_id: int, texto: str, passo: str, dados: dict, fluxo: dict) -> None:
        if passo == "email":
            dados["email"] = texto
            fluxo["passo"] = "senha"
            self.enviar(chat_id, "Digite sua senha:", None)
        elif passo == "senha":
            dados["senha"] = texto
            resp = self.api("POST", "/auth/login", json=dados)
            self.fluxos.pop(chat_id, None)
            if resp.status_code == 200:
                jwt_token = resp.json()["access_token"]
                user_id = extrair_user_id(jwt_token)
                if user_id is None:
                    self.enviar(chat_id, "Não foi possível identificar o usuário no token.", None)
                    self.mostrar_menu(chat_id, "inicial")
                    return
                self.sessoes[chat_id] = {"jwt": jwt_token, "user_id": user_id}
                self.enviar(chat_id, "[Logou]", None)
                self.mostrar_menu(chat_id, "principal")
            else:
                self.enviar(chat_id, detalhe_erro(resp), None)
                self.mostrar_menu(chat_id, "inicial")

    def continuar_nova_tarefa(self, chat_id: int, texto: str, passo: str, dados: dict, fluxo: dict) -> None:
        if passo == "titulo":
            dados["titulo"] = texto
            fluxo["passo"] = "descricao"
            self.enviar(chat_id, "Descreva a tarefa:", None)
        elif passo == "descricao":
            dados["descricao"] = texto
            fluxo["passo"] = "prioridade"
            self.enviar(chat_id, "Qual a prioridade?", PRIORIDADES)
        elif passo == "prioridade":
            if texto not in PRIORIDADES:
                self.enviar(chat_id, "Escolha uma das opções:", PRIORIDADES)
                return
            dados["prioridade"] = texto
            dados["usuario_id"] = self.sessoes[chat_id]["user_id"]
            resp = self.api("POST", "/tasks", chat_id=chat_id, json=dados)
            self.fluxos.pop(chat_id, None)
            if resp.status_code == 201:
                tarefa = resp.json()
                self.enviar(chat_id, f"Tarefa #{tarefa['id']} criada: {tarefa['titulo']}", None)
            else:
                self.enviar(chat_id, detalhe_erro(resp), None)
            self.mostrar_menu(chat_id, "tarefas")

    def continuar_edicao_perfil(self, chat_id: int, texto: str, passo: str, dados: dict, fluxo: dict) -> None:
        if passo == "campo":
            if texto not in CAMPO_KEY:
                self.enviar(chat_id, "Escolha um campo:", list(CAMPO_KEY) + ["Voltar"])
                return
            dados["campo"] = CAMPO_KEY[texto]
            fluxo["passo"] = "valor"
            self.enviar(chat_id, "Digite o novo valor:", None)
        elif passo == "valor":
            user_id = self.sessoes[chat_id]["user_id"]
            resp = self.api("PUT", f"/users/{user_id}", chat_id=chat_id, json={dados["campo"]: texto})
            self.fluxos.pop(chat_id, None)
            if resp.status_code == 200:
                self.enviar(chat_id, "Perfil atualizado.", None)
            else:
                self.enviar(chat_id, detalhe_erro(resp), None)
            self.mostrar_menu(chat_id, "conta")

    def continuar_exclusao_conta(self, chat_id: int, texto: str, passo: str) -> None:
        if passo != "confirmar":
            return
        if texto != "Sim, excluir":
            self.fluxos.pop(chat_id, None)
            self.enviar(chat_id, "Exclusão cancelada.", None)
            self.mostrar_menu(chat_id, "conta")
            return

        user_id = self.sessoes[chat_id]["user_id"]
        resp = self.api("DELETE", f"/users/{user_id}", chat_id=chat_id)
        self.fluxos.pop(chat_id, None)
        if resp.status_code == 204:
            self.enviar(chat_id, "Conta excluída.", None)
            self.cmd_logout(chat_id)
        else:
            self.enviar(chat_id, detalhe_erro(resp), None)
            self.mostrar_menu(chat_id, "conta")

    def rotear(self, chat_id: int, texto: str) -> None:
        estado = self.menus.get(chat_id, "inicial")

        if estado == "inicial":
            if texto == "Criar conta":
                self.iniciar_fluxo(chat_id, "criar")
            elif texto == "Login":
                self.iniciar_fluxo(chat_id, "login")
            else:
                self.mostrar_menu(chat_id, "inicial")
        elif estado == "principal":
            if texto == "Tarefas":
                self.mostrar_menu(chat_id, "tarefas")
            elif texto == "Conta":
                self.mostrar_menu(chat_id, "conta")
            elif texto == "Logout":
                self.cmd_logout(chat_id)
            else:
                self.mostrar_menu(chat_id, "principal")
        elif estado == "tarefas":
            if texto == "Listar tarefas":
                self.acao_listar_tarefas(chat_id)
            elif texto == "Nova tarefa":
                self.iniciar_fluxo(chat_id, "novatarefa")
            elif texto == "Voltar":
                self.mostrar_menu(chat_id, "principal")
            else:
                self.mostrar_menu(chat_id, "tarefas")
        elif estado == "conta":
            if texto == "Meu perfil":
                self.acao_meu_perfil(chat_id)
            elif texto == "Atualizar perfil":
                self.iniciar_fluxo(chat_id, "editar_perfil")
            elif texto == "Excluir conta":
                self.iniciar_fluxo(chat_id, "excluir_conta")
            elif texto == "Voltar":
                self.mostrar_menu(chat_id, "principal")
            else:
                self.mostrar_menu(chat_id, "conta")
        else:
            self.mostrar_menu(chat_id, self.menu_logado(chat_id))

    def tratar(self, update: dict) -> None:
        mensagem = update.get("message")
        if not mensagem or "text" not in mensagem:
            return

        chat_id = mensagem["chat"]["id"]
        texto = mensagem["text"].strip()

        if texto == "/start":
            self.cmd_start(chat_id)
            return

        if chat_id in self.fluxos:
            if texto in ("Voltar", "Cancelar"):
                self.fluxos.pop(chat_id, None)
                self.mostrar_menu(chat_id, self.menus.get(chat_id, self.menu_logado(chat_id)))
                return
            self.continuar_fluxo(chat_id, texto)
            return

        self.rotear(chat_id, texto)
