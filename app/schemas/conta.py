from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ContaResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Identificador da conta, usado nas rotas de transação e extrato")
    agencia: str = Field(description="Número da agência", examples=["0001"])
    numero: str = Field(description="Número da conta corrente", examples=["123456"])
    saldo: Decimal = Field(description="Saldo atual da conta", examples=["250.00"])
    criada_em: datetime = Field(description="Data de abertura da conta (UTC)")
