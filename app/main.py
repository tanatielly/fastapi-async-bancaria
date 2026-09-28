from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models  # noqa: F401 - importa os models para o create_all enxergar as tabelas
from app.database import criar_tabelas
from app.routers import auth, contas, transacoes

descricao = """
API assíncrona para gerenciar **depósitos** e **saques** em contas correntes,
com exibição de **extrato**. As rotas de contas e transações exigem autenticação via **JWT**.

## Como usar

1. Cadastre um usuário em `POST /auth/cadastro`
2. Clique no botão **Authorize** e informe o e-mail (no campo *username*) e a senha
3. Abra uma conta corrente em `POST /contas`
4. Faça depósitos e saques em `POST /contas/{conta_id}/transacoes`
5. Veja o extrato em `GET /contas/{conta_id}/extrato`

## Regras

- Não são aceitos depósitos nem saques com valor negativo ou zero
- Só é possível sacar se a conta tiver saldo suficiente
- Cada usuário só enxerga as próprias contas

Os valores em dinheiro são retornados como texto (ex.: `"150.00"`) para não perder precisão.
"""

tags = [
    {"name": "Autenticação", "description": "Cadastro de usuários e login (geração do token JWT)."},
    {"name": "Contas", "description": "Abertura e consulta das contas correntes do usuário logado."},
    {"name": "Transações", "description": "Depósitos, saques e extrato de uma conta corrente."},
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # cria as tabelas quando a aplicação sobe
    await criar_tabelas()
    yield


app = FastAPI(
    title="API Bancária Assíncrona",
    description=descricao,
    version="1.0.0",
    openapi_tags=tags,
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(contas.router)
app.include_router(transacoes.router)


@app.get("/", include_in_schema=False)
async def raiz():
    return {"mensagem": "API Bancária no ar! Acesse /docs para ver a documentação."}
