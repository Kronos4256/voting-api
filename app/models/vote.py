from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, CreatedAt


class Vote(Base):
    __tablename__ = "votes"

    id: Mapped[int] = mapped_column(primary_key=True)
    voter_id: Mapped[int] = mapped_column(ForeignKey("voters.id"), unique=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), index=True)
    created_at: Mapped[CreatedAt]
