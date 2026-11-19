from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ConflictError
from app.models import Candidate
from app.schemas.candidate import CandidateCreate, CandidateQuery
from app.services.queries import PageResult, get_or_raise, paginate
from app.services.registration import reserve_email


async def register_candidate(session: AsyncSession, data: CandidateCreate) -> Candidate:
    await reserve_email(session, data.email)
    candidate = Candidate(**data.model_dump())
    session.add(candidate)
    await session.commit()
    return candidate


async def list_candidates(session: AsyncSession, query: CandidateQuery) -> PageResult[Candidate]:
    statement = select(Candidate).order_by(Candidate.id)
    if query.name:
        statement = statement.where(Candidate.name.icontains(query.name, autoescape=True))
    if query.party:
        statement = statement.where(Candidate.party.icontains(query.party, autoescape=True))
    return await paginate(session, statement, query)


async def get_candidate(session: AsyncSession, candidate_id: int) -> Candidate:
    return await get_or_raise(session, Candidate, candidate_id)


async def delete_candidate(session: AsyncSession, candidate_id: int) -> None:
    deleted_id = await session.scalar(
        delete(Candidate)
        .where(Candidate.id == candidate_id, Candidate.votes == 0)
        .returning(Candidate.id)
    )
    if deleted_id is None:
        await get_or_raise(session, Candidate, candidate_id)
        raise ConflictError("Candidate has received votes and cannot be deleted")
    await session.commit()
