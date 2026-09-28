async def test_cadastrar_usuario(cliente):
    resposta = await cliente.post(
        "/auth/cadastro",
        json={"nome": "Maria", "email": "maria@email.com", "senha": "senha123"},
    )

    assert resposta.status_code == 201
    dados = resposta.json()
    assert dados["email"] == "maria@email.com"
    # a senha nunca pode voltar na resposta
    assert "senha" not in dados
    assert "senha_hash" not in dados


async def test_nao_cadastra_email_repetido(cliente):
    usuario = {"nome": "Maria", "email": "maria@email.com", "senha": "senha123"}
    await cliente.post("/auth/cadastro", json=usuario)

    resposta = await cliente.post("/auth/cadastro", json=usuario)

    assert resposta.status_code == 409


async def test_nao_cadastra_senha_curta(cliente):
    resposta = await cliente.post(
        "/auth/cadastro",
        json={"nome": "Maria", "email": "maria@email.com", "senha": "123"},
    )

    assert resposta.status_code == 422


async def test_login(cliente):
    await cliente.post(
        "/auth/cadastro",
        json={"nome": "Maria", "email": "maria@email.com", "senha": "senha123"},
    )

    resposta = await cliente.post(
        "/auth/login", data={"username": "maria@email.com", "password": "senha123"}
    )

    assert resposta.status_code == 200
    assert resposta.json()["token_type"] == "bearer"
    assert resposta.json()["access_token"]


async def test_login_com_senha_errada(cliente):
    await cliente.post(
        "/auth/cadastro",
        json={"nome": "Maria", "email": "maria@email.com", "senha": "senha123"},
    )

    resposta = await cliente.post(
        "/auth/login", data={"username": "maria@email.com", "password": "errada"}
    )

    assert resposta.status_code == 401


async def test_ver_usuario_logado(cliente, headers):
    resposta = await cliente.get("/auth/me", headers=headers)

    assert resposta.status_code == 200
    assert resposta.json()["email"] == "maria@email.com"


async def test_rota_protegida_sem_token(cliente):
    resposta = await cliente.get("/contas")

    assert resposta.status_code == 401


async def test_rota_protegida_com_token_invalido(cliente):
    resposta = await cliente.get("/contas", headers={"Authorization": "Bearer token-falso"})

    assert resposta.status_code == 401
