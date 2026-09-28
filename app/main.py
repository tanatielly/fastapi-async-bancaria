from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import criar_tabelas


@asynccontextmanager
async def lifespan(app: FastAPI):
    # cria as tabelas quando a aplicação sobe
    await criar_tabelas()
    yield


app = FastAPI(title="API Bancária Assíncrona", lifespan=lifespan)


@app.get("/")
async def raiz():
    return {"mensagem": "API Bancária no ar!"}
