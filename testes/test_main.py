def test_read_root(client):
    # Faz uma requisição GET simulada para a raiz
    response = client.get("/")
    
    # Verifica se o código de status HTTP é 200 (OK)
    assert response.status_code == 200
    
    # Verifica se o corpo da resposta em JSON é exatamente o esperado
    assert response.json() == {"Status": "Running"}