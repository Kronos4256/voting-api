from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, CreatedAt


class Candidate(Base):
    __tablename__ = "candidates"
    __table_args__ = (CheckConstraint("votes >= 0", name="votes_non_negative"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(254), unique=True)
    party: Mapped[str | None] = mapped_column(String(120))
    votes: Mapped[int] = mapped_column(default=0, server_default="0")
    created_at: Mapped[CreatedAt]
