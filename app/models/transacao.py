import enum
from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.conta import Conta


class TipoTransacao(str, enum.Enum):
    deposito = "deposito"
    saque = "saque"


class Transacao(Base):
    __tablename__ = "transacoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    conta_id: Mapped[int] = mapped_column(ForeignKey("contas.id"), index=True)
    tipo: Mapped[TipoTransacao] = mapped_column(Enum(TipoTransacao))
    valor: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    descricao: Mapped[str | None] = mapped_column(String(200))
    criada_em: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    conta: Mapped["Conta"] = relationship(back_populates="transacoes")
