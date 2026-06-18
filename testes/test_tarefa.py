import pytest
from datetime import date

def get_token(client, email, senha):
    res = client.post("/auth/login", json={"email": email, "senha": senha})
    return res.json()["access_token"]

def test_crud_tarefa(client):
    # Setup: Criar usuário e logar
    client.post("/users", json={"nome": "User Task", "email": "task@teste.com", "senha": "123"})
    token = get_token(client, "task@teste.com", "123")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Criar Tarefa
    res_create = client.post(
        "/tasks",
        headers=headers,
        json={
            "titulo": "Minha Tarefa",
            "descricao": "Descricao da tarefa",
            "prioridade": "alta"
        }
    )
    assert res_create.status_code == 201
    tarefa_id = res_create.json()["id"]

    # 2. Ler Tarefa
    res_get = client.get(f"/tasks/{tarefa_id}", headers=headers)
    assert res_get.status_code == 200
    assert res_get.json()["titulo"] == "Minha Tarefa"

    # 3. Atualizar Tarefa
    res_put = client.put(
        f"/tasks/{tarefa_id}",
        headers=headers,
        json={"status": "concluida"}
    )
    assert res_put.status_code == 200
    assert res_put.json()["status"] == "concluida"

    # 4. Deletar Tarefa
    res_del = client.delete(f"/tasks/{tarefa_id}", headers=headers)
    assert res_del.status_code == 204

def test_permissao_tarefa(client):
    # Usuário A
    client.post("/users", json={"nome": "User A", "email": "a@teste.com", "senha": "123"})
    token_a = get_token(client, "a@teste.com", "123")
    user_a_id = client.get("/users/1", headers={"Authorization": f"Bearer {token_a}"}).json()["id"] # O primeiro id costuma ser 1, mas vamos garantir

    # Usuário B
    client.post("/users", json={"nome": "User B", "email": "b@teste.com", "senha": "123"})
    token_b = get_token(client, "b@teste.com", "123")

    # A cria uma tarefa para si
    res_task = client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"titulo": "Task de A", "descricao": "...", "usuario_id": user_a_id}
    )
    task_id = res_task.json()["id"]

    # B tenta deletar a tarefa de A
    res_del = client.delete(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert res_del.status_code == 403

def test_filtros_tarefa(client):
    client.post("/users", json={"nome": "User Filtro", "email": "filtro@teste.com", "senha": "123"})
    token = get_token(client, "filtro@teste.com", "123")
    headers = {"Authorization": f"Bearer {token}"}

    # Criar tarefas com estados diferentes
    client.post("/tasks", headers=headers, json={"titulo": "T1", "descricao": "...", "status": "pendente", "prioridade": "baixa"})
    client.post("/tasks", headers=headers, json={"titulo": "T2", "descricao": "...", "status": "concluida", "prioridade": "alta"})

    # Filtrar por status
    res_status = client.get("/tasks?status=concluida", headers=headers)
    assert len(res_status.json()) == 1
    assert res_status.json()[0]["titulo"] == "T2"

    # Filtrar por prioridade
    res_prioridade = client.get("/tasks?priority=baixa", headers=headers)
    assert len(res_prioridade.json()) == 1
    assert res_prioridade.json()[0]["titulo"] == "T1"
