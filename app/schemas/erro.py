from pydantic import BaseModel, Field


class MensagemErro(BaseModel):
    """Formato padrão dos erros retornados pela API (o mesmo do HTTPException)."""

    detail: str = Field(description="Mensagem explicando o erro", examples=["Conta não encontrada."])
