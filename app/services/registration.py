from sqlalchemy import exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ConflictError
from app.models import Candidate, Voter


async def reserve_email(session: AsyncSession, email: str) -> None:
    await session.execute(select(func.pg_advisory_xact_lock(func.hashtext(email))))

    if await session.scalar(select(exists().where(Voter.email == email))):
        raise ConflictError("Email is already registered as a voter")
    if await session.scalar(select(exists().where(Candidate.email == email))):
        raise ConflictError("Email is already registered as a candidate")
