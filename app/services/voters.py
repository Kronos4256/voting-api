from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ConflictError
from app.models import Voter
from app.schemas.voter import VoterCreate, VoterQuery
from app.services.queries import PageResult, get_or_raise, paginate
from app.services.registration import reserve_email


async def register_voter(session: AsyncSession, data: VoterCreate) -> Voter:
    await reserve_email(session, data.email)
    voter = Voter(**data.model_dump())
    session.add(voter)
    await session.commit()
    return voter


async def list_voters(session: AsyncSession, query: VoterQuery) -> PageResult[Voter]:
    statement = select(Voter).order_by(Voter.id)
    if query.name:
        statement = statement.where(Voter.name.icontains(query.name, autoescape=True))
    if query.has_voted is not None:
        statement = statement.where(Voter.has_voted.is_(query.has_voted))
    return await paginate(session, statement, query)


async def get_voter(session: AsyncSession, voter_id: int) -> Voter:
    return await get_or_raise(session, Voter, voter_id)


async def delete_voter(session: AsyncSession, voter_id: int) -> None:
    deleted_id = await session.scalar(
        delete(Voter).where(Voter.id == voter_id, Voter.has_voted.is_(False)).returning(Voter.id)
    )
    if deleted_id is None:
        await get_or_raise(session, Voter, voter_id)
        raise ConflictError("Voter has already voted and cannot be deleted")
    await session.commit()
