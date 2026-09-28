from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.database import SessaoDep
from app.models import TipoTransacao, Transacao
from app.routers.contas import buscar_conta_do_usuario
from app.schemas.erro import MensagemErro
from app.schemas.transacao import ExtratoResposta, TransacaoCriar, TransacaoResposta
from app.seguranca import UsuarioAtual

router = APIRouter(
    prefix="/contas/{conta_id}",
    tags=["Transações"],
    responses={
        401: {"model": MensagemErro, "description": "Token ausente, inválido ou expirado"},
        404: {"model": MensagemErro, "description": "Conta não encontrada"},
    },
)


@router.post(
    "/transacoes",
    response_model=TransacaoResposta,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar depósito ou saque",
    responses={400: {"model": MensagemErro, "description": "Saldo insuficiente para o saque"}},
)
async def criar_transacao(
    conta_id: int, dados: TransacaoCriar, usuario: UsuarioAtual, sessao: SessaoDep
):
    """
    Registra uma transação na conta e atualiza o saldo.

    - **deposito**: soma o valor ao saldo
    - **saque**: subtrai o valor do saldo, só é permitido se houver saldo suficiente

    O valor precisa ser maior que zero, valores negativos ou zerados retornam **422**.
    """
    conta = await buscar_conta_do_usuario(sessao, conta_id, usuario)

    if dados.tipo == TipoTransacao.saque:
        if dados.valor > conta.saldo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Saldo insuficiente para realizar o saque.",
            )
        conta.saldo -= dados.valor
    else:
        conta.saldo += dados.valor

    transacao = Transacao(
        conta_id=conta.id,
        tipo=dados.tipo,
        valor=dados.valor,
        descricao=dados.descricao,
    )
    sessao.add(transacao)
    # o saldo da conta e a transação são salvos juntos no mesmo commit
    await sessao.commit()
    await sessao.refresh(transacao)
    return transacao


@router.get("/extrato", response_model=ExtratoResposta, summary="Exibir extrato")
async def exibir_extrato(conta_id: int, usuario: UsuarioAtual, sessao: SessaoDep):
    """
    Exibe o extrato da conta: os dados da conta com o saldo atual e todas as
    transações realizadas, em ordem cronológica.
    """
    conta = await buscar_conta_do_usuario(sessao, conta_id, usuario)

    # busca as transações direto no banco em vez de usar conta.transacoes,
    # porque lazy loading não funciona com sessão assíncrona
    resultado = await sessao.execute(
        select(Transacao)
        .where(Transacao.conta_id == conta.id)
        .order_by(Transacao.criada_em, Transacao.id)
    )

    return {"conta": conta, "transacoes": resultado.scalars().all()}
