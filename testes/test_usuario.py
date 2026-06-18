def test_criar_usuario(client):
    # Simula o envio de um POST para o endpoint de usuários
    response = client.post(
        "/users",
        json={
            "nome": "Teste",
            "email": "luiz@teste.com",
            "senha": "senha_super_segura"
        }
    )
    
    # Verifica se o status é 201 Created
    assert response.status_code == 201
    
    # Extrai o retorno
    dados = response.json()
    
    # Valida se os dados voltaram corretamente no response_model (UsuarioResponse)
    assert dados["nome"] == "Teste"
    assert dados["email"] == "luiz@teste.com"
    assert "id" in dados
    assert "senha" not in dados # Garante que a senha não está vazando na resposta

def test_atualizar_usuario(client):
    # Criar usuário
    res = client.post("/users", json={"nome": "Antigo", "email": "antigo@teste.com", "senha": "123"})
    user_id = res.json()["id"]
    
    # Login
    login_res = client.post("/auth/login", json={"email": "antigo@teste.com", "senha": "123"})
    token = login_res.json()["access_token"]
    
    # Atualizar
    response = client.put(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"nome": "Novo Nome"}
    )
    assert response.status_code == 200
    assert response.json()["nome"] == "Novo Nome"

def test_soft_delete_usuario(client):
    # Criar usuário
    res = client.post("/users", json={"nome": "Deletar", "email": "deletar@teste.com", "senha": "123"})
    user_id = res.json()["id"]
    
    # Login
    login_res = client.post("/auth/login", json={"email": "deletar@teste.com", "senha": "123"})
    token = login_res.json()["access_token"]
    
    # Deletar
    response = client.delete(f"/users/{user_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204
    
    # Tentar logar com usuário deletado
    login_fail = client.post("/auth/login", json={"email": "deletar@teste.com", "senha": "123"})
    assert login_fail.status_code == 401