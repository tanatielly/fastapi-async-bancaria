from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.transacao import TipoTransacao


class TransacaoCriar(BaseModel):
    tipo: TipoTransacao
    # gt=0 já barra valores negativos e zerados
    valor: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    descricao: str | None = Field(default=None, max_length=200)


class TransacaoResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    conta_id: int
    tipo: TipoTransacao
    valor: Decimal
    descricao: str | None
    criada_em: datetime
