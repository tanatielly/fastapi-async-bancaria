from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models  # noqa: F401 - importa os models para o create_all enxergar as tabelas
from app.database import criar_tabelas
from app.routers import auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    # cria as tabelas quando a aplicação sobe
    await criar_tabelas()
    yield


app = FastAPI(title="API Bancária Assíncrona", lifespan=lifespan)

app.include_router(auth.router)


@app.get("/")
async def raiz():
    return {"mensagem": "API Bancária no ar!"}
