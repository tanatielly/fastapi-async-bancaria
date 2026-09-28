from decimal import Decimal

import pytest


async def fazer_transacao(cliente, headers, conta_id, tipo, valor):
    return await cliente.post(
        f"/contas/{conta_id}/transacoes",
        headers=headers,
        json={"tipo": tipo, "valor": valor},
    )


async def buscar_saldo(cliente, headers, conta_id):
    resposta = await cliente.get(f"/contas/{conta_id}", headers=headers)
    return Decimal(resposta.json()["saldo"])


async def test_deposito_atualiza_saldo(cliente, headers, conta):
    resposta = await fazer_transacao(cliente, headers, conta["id"], "deposito", "100.50")

    assert resposta.status_code == 201
    assert resposta.json()["tipo"] == "deposito"
    assert await buscar_saldo(cliente, headers, conta["id"]) == Decimal("100.50")


async def test_saque_com_saldo(cliente, headers, conta):
    await fazer_transacao(cliente, headers, conta["id"], "deposito", "100")

    resposta = await fazer_transacao(cliente, headers, conta["id"], "saque", "40")

    assert resposta.status_code == 201
    assert await buscar_saldo(cliente, headers, conta["id"]) == Decimal("60")


async def test_saque_sem_saldo(cliente, headers, conta):
    await fazer_transacao(cliente, headers, conta["id"], "deposito", "50")

    resposta = await fazer_transacao(cliente, headers, conta["id"], "saque", "50.01")

    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "Saldo insuficiente para realizar o saque."
    # o saldo não pode ter mudado
    assert await buscar_saldo(cliente, headers, conta["id"]) == Decimal("50")


async def test_saque_de_todo_o_saldo(cliente, headers, conta):
    await fazer_transacao(cliente, headers, conta["id"], "deposito", "50")

    resposta = await fazer_transacao(cliente, headers, conta["id"], "saque", "50")

    assert resposta.status_code == 201
    assert await buscar_saldo(cliente, headers, conta["id"]) == 0


@pytest.mark.parametrize("tipo", ["deposito", "saque"])
@pytest.mark.parametrize("valor", ["-10", "0"])
async def test_nao_aceita_valor_negativo_ou_zero(cliente, headers, conta, tipo, valor):
    resposta = await fazer_transacao(cliente, headers, conta["id"], tipo, valor)

    assert resposta.status_code == 422


async def test_nao_aceita_mais_de_duas_casas_decimais(cliente, headers, conta):
    resposta = await fazer_transacao(cliente, headers, conta["id"], "deposito", "10.555")

    assert resposta.status_code == 422


async def test_nao_aceita_tipo_invalido(cliente, headers, conta):
    resposta = await fazer_transacao(cliente, headers, conta["id"], "pix", "10")

    assert resposta.status_code == 422


async def test_transacao_em_conta_de_outro_usuario(cliente, conta, logar):
    headers_outro = await logar(email="joao@email.com")

    resposta = await fazer_transacao(cliente, headers_outro, conta["id"], "deposito", "10")

    assert resposta.status_code == 404


async def test_transacao_em_conta_inexistente(cliente, headers):
    resposta = await fazer_transacao(cliente, headers, 999, "deposito", "10")

    assert resposta.status_code == 404


async def test_extrato(cliente, headers, conta):
    await fazer_transacao(cliente, headers, conta["id"], "deposito", "100")
    await fazer_transacao(cliente, headers, conta["id"], "saque", "30.50")

    resposta = await cliente.get(f"/contas/{conta['id']}/extrato", headers=headers)

    assert resposta.status_code == 200
    extrato = resposta.json()
    assert Decimal(extrato["conta"]["saldo"]) == Decimal("69.50")
    assert [t["tipo"] for t in extrato["transacoes"]] == ["deposito", "saque"]
    assert Decimal(extrato["transacoes"][1]["valor"]) == Decimal("30.50")


async def test_extrato_de_conta_sem_transacoes(cliente, headers, conta):
    resposta = await cliente.get(f"/contas/{conta['id']}/extrato", headers=headers)

    assert resposta.status_code == 200
    assert resposta.json()["transacoes"] == []


async def test_extrato_de_conta_de_outro_usuario(cliente, conta, logar):
    headers_outro = await logar(email="joao@email.com")

    resposta = await cliente.get(f"/contas/{conta['id']}/extrato", headers=headers_outro)

    assert resposta.status_code == 404
