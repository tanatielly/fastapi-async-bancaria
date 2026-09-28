from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.transacao import Transacao
    from app.models.usuario import Usuario


class Conta(Base):
    __tablename__ = "contas"

    id: Mapped[int] = mapped_column(primary_key=True)
    agencia: Mapped[str] = mapped_column(String(4), default="0001")
    numero: Mapped[str] = mapped_column(String(6), unique=True)
    saldo: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    criada_em: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    usuario: Mapped["Usuario"] = relationship(back_populates="contas")
    # uma conta pode ter várias transações (depósitos e saques)
    transacoes: Mapped[list["Transacao"]] = relationship(back_populates="conta")
