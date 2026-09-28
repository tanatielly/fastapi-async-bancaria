import random

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import SessaoDep
from app.models import Conta, Usuario
from app.schemas.conta import ContaResposta
from app.schemas.erro import MensagemErro
from app.seguranca import UsuarioAtual

router = APIRouter(
    prefix="/contas",
    tags=["Contas"],
    responses={401: {"model": MensagemErro, "description": "Token ausente, inválido ou expirado"}},
)


async def gerar_numero_conta(sessao: AsyncSession) -> str:
    # sorteia um número de 6 dígitos que ainda não esteja sendo usado
    while True:
        numero = f"{random.randint(0, 999999):06d}"
        resultado = await sessao.execute(select(Conta.id).where(Conta.numero == numero))
        if resultado.scalar_one_or_none() is None:
            return numero


async def buscar_conta_do_usuario(sessao: AsyncSession, conta_id: int, usuario: Usuario) -> Conta:
    """Busca a conta garantindo que ela pertence ao usuário logado."""
    resultado = await sessao.execute(
        select(Conta).where(Conta.id == conta_id, Conta.usuario_id == usuario.id)
    )
    conta = resultado.scalar_one_or_none()

    # se a conta for de outro usuário também retorna 404, pra não expor que ela existe
    if conta is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conta não encontrada.")

    return conta


@router.post(
    "",
    response_model=ContaResposta,
    status_code=status.HTTP_201_CREATED,
    summary="Abrir conta corrente",
)
async def abrir_conta(usuario: UsuarioAtual, sessao: SessaoDep):
    """
    Abre uma nova conta corrente para o usuário logado.

    A conta começa com saldo zero, na agência `0001`, e recebe um número aleatório de 6 dígitos.
    Um mesmo usuário pode ter mais de uma conta.
    """
    conta = Conta(numero=await gerar_numero_conta(sessao), usuario_id=usuario.id)
    sessao.add(conta)
    await sessao.commit()
    await sessao.refresh(conta)
    return conta


@router.get("", response_model=list[ContaResposta], summary="Listar minhas contas")
async def listar_contas(usuario: UsuarioAtual, sessao: SessaoDep):
    """Lista todas as contas correntes do usuário logado."""
    resultado = await sessao.execute(
        select(Conta).where(Conta.usuario_id == usuario.id).order_by(Conta.id)
    )
    return resultado.scalars().all()


@router.get(
    "/{conta_id}",
    response_model=ContaResposta,
    summary="Consultar conta",
    responses={404: {"model": MensagemErro, "description": "Conta não encontrada"}},
)
async def detalhar_conta(conta_id: int, usuario: UsuarioAtual, sessao: SessaoDep):
    """Mostra os dados de uma conta do usuário logado, incluindo o saldo atual."""
    return await buscar_conta_do_usuario(sessao, conta_id, usuario)
