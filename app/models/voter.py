from sqlalchemy import String, false
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, CreatedAt


class Voter(Base):
    __tablename__ = "voters"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(254), unique=True)
    has_voted: Mapped[bool] = mapped_column(default=False, server_default=false())
    created_at: Mapped[CreatedAt]
