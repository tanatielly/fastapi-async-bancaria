import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.database import Base, get_sessao
from app.main import app


@pytest.fixture
async def cliente():
    # banco em memória só para os testes, recriado do zero em cada teste.
    # o StaticPool faz todas as sessões usarem a mesma conexão (senão cada uma teria um banco vazio)
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", poolclass=StaticPool)
    async with engine.begin() as conexao:
        await conexao.run_sync(Base.metadata.create_all)

    SessaoTeste = async_sessionmaker(engine, expire_on_commit=False)

    async def get_sessao_teste():
        async with SessaoTeste() as sessao:
            yield sessao

    app.dependency_overrides[get_sessao] = get_sessao_teste

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://teste") as cliente:
        yield cliente

    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.fixture
def logar(cliente):
    """Cadastra um usuário, faz login e devolve o header com o token."""

    async def _logar(email="maria@email.com", senha="senha123"):
        await cliente.post(
            "/auth/cadastro", json={"nome": "Maria", "email": email, "senha": senha}
        )
        resposta = await cliente.post("/auth/login", data={"username": email, "password": senha})
        return {"Authorization": f"Bearer {resposta.json()['access_token']}"}

    return _logar


@pytest.fixture
async def headers(logar):
    return await logar()


@pytest.fixture
async def conta(cliente, headers):
    resposta = await cliente.post("/contas", headers=headers)
    return resposta.json()
