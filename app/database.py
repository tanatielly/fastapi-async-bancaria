from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import configuracoes

engine = create_async_engine(configuracoes.url_banco)

SessaoLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_sessao():
    """Dependência que abre uma sessão com o banco para cada requisição."""
    async with SessaoLocal() as sessao:
        yield sessao


async def criar_tabelas():
    async with engine.begin() as conexao:
        await conexao.run_sync(Base.metadata.create_all)
