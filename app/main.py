from fastapi import FastAPI

app = FastAPI(title="API Bancária Assíncrona")


@app.get("/")
async def raiz():
    return {"mensagem": "API Bancária no ar!"}
