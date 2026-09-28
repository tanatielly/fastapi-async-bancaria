from decimal import Decimal


async def test_abrir_conta(cliente, headers):
    resposta = await cliente.post("/contas", headers=headers)

    assert resposta.status_code == 201
    conta = resposta.json()
    assert conta["agencia"] == "0001"
    assert len(conta["numero"]) == 6
    assert Decimal(conta["saldo"]) == 0


async def test_listar_contas(cliente, headers):
    await cliente.post("/contas", headers=headers)
    await cliente.post("/contas", headers=headers)

    resposta = await cliente.get("/contas", headers=headers)

    assert resposta.status_code == 200
    assert len(resposta.json()) == 2


async def test_consultar_conta(cliente, headers, conta):
    resposta = await cliente.get(f"/contas/{conta['id']}", headers=headers)

    assert resposta.status_code == 200
    assert resposta.json()["numero"] == conta["numero"]


async def test_nao_ve_conta_de_outro_usuario(cliente, conta, logar):
    headers_outro = await logar(email="joao@email.com")

    resposta = await cliente.get(f"/contas/{conta['id']}", headers=headers_outro)
    assert resposta.status_code == 404

    resposta = await cliente.get("/contas", headers=headers_outro)
    assert resposta.json() == []
