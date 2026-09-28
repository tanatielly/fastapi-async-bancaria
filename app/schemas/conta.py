from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ContaResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    agencia: str
    numero: str
    saldo: Decimal
    criada_em: datetime
