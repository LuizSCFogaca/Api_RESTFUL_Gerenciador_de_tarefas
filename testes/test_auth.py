import pytest

def test_login_sucesso(client):
    # Primeiro criamos um usuário para testar o login
    client.post(
        "/users",
        json={
            "nome": "User Auth",
            "email": "auth@teste.com",
            "senha": "password123"
        }
    )
    
    # Tenta fazer login
    response = client.post(
        "/auth/login",
        json={
            "email": "auth@teste.com",
            "senha": "password123"
        }
    )
    
    assert response.status_code == 200
    dados = response.json()
    assert "access_token" in dados
    assert dados["token_type"] == "bearer"

def test_login_senha_invalida(client):
    # Criamos o usuário
    client.post(
        "/users",
        json={
            "nome": "User Auth 2",
            "email": "auth2@teste.com",
            "senha": "password123"
        }
    )
    
    # Login com senha errada
    response = client.post(
        "/auth/login",
        json={
            "email": "auth2@teste.com",
            "senha": "senha_errada"
        }
    )
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Email ou senha inválidos"

def test_logout(client):
    # Login para pegar o token
    client.post("/users", json={"nome": "User Logout", "email": "logout@teste.com", "senha": "123"})
    login_res = client.post("/auth/login", json={"email": "logout@teste.com", "senha": "123"})
    token = login_res.json()["access_token"]
    
    # Logout (rota protegida)
    response = client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json() == {"mensagem": "Logout realizado com sucesso"}

def test_acesso_sem_token(client):
    # Tenta acessar logout sem token
    response = client.post("/auth/logout")
    assert response.status_code == 401
