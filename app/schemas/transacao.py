from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.transacao import TipoTransacao
from app.schemas.conta import ContaResposta


class TransacaoCriar(BaseModel):
    tipo: TipoTransacao = Field(description="Tipo da transação: `deposito` ou `saque`")
    # gt=0 já barra valores negativos e zerados
    valor: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
        description="Valor da transação. Precisa ser maior que zero e ter no máximo 2 casas decimais",
        examples=["150.00"],
    )
    descricao: str | None = Field(
        default=None,
        max_length=200,
        description="Descrição opcional da transação",
        examples=["Pagamento do salário"],
    )


class TransacaoResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Identificador da transação")
    conta_id: int = Field(description="Conta onde a transação foi feita")
    tipo: TipoTransacao
    valor: Decimal = Field(examples=["150.00"])
    descricao: str | None
    criada_em: datetime = Field(description="Data e hora da transação (UTC)")


class ExtratoResposta(BaseModel):
    conta: ContaResposta = Field(description="Dados da conta, incluindo o saldo atual")
    transacoes: list[TransacaoResposta] = Field(
        description="Transações da conta, da mais antiga para a mais recente"
    )
