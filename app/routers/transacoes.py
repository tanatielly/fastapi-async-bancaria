from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.database import SessaoDep
from app.models import TipoTransacao, Transacao
from app.routers.contas import buscar_conta_do_usuario
from app.schemas.transacao import ExtratoResposta, TransacaoCriar, TransacaoResposta
from app.seguranca import UsuarioAtual

router = APIRouter(prefix="/contas/{conta_id}", tags=["Transações"])


@router.post("/transacoes", response_model=TransacaoResposta, status_code=status.HTTP_201_CREATED)
async def criar_transacao(
    conta_id: int, dados: TransacaoCriar, usuario: UsuarioAtual, sessao: SessaoDep
):
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


@router.get("/extrato", response_model=ExtratoResposta)
async def exibir_extrato(conta_id: int, usuario: UsuarioAtual, sessao: SessaoDep):
    conta = await buscar_conta_do_usuario(sessao, conta_id, usuario)

    # busca as transações direto no banco em vez de usar conta.transacoes,
    # porque lazy loading não funciona com sessão assíncrona
    resultado = await sessao.execute(
        select(Transacao)
        .where(Transacao.conta_id == conta.id)
        .order_by(Transacao.criada_em, Transacao.id)
    )

    return {"conta": conta, "transacoes": resultado.scalars().all()}
