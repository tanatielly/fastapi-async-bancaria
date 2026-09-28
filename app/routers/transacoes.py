from fastapi import APIRouter, HTTPException, status

from app.database import SessaoDep
from app.models import TipoTransacao, Transacao
from app.routers.contas import buscar_conta_do_usuario
from app.schemas.transacao import TransacaoCriar, TransacaoResposta
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
