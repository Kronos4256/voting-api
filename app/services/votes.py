from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ConflictError, NotFoundError
from app.models import Candidate, Vote, Voter
from app.schemas.common import PageParams
from app.schemas.vote import CandidateResult, VoteCreate, VotingStatistics
from app.services.queries import PageResult, get_or_raise, paginate


async def cast_vote(session: AsyncSession, data: VoteCreate) -> Vote:
    marked_voter_id = await session.scalar(
        update(Voter)
        .where(Voter.id == data.voter_id, Voter.has_voted.is_(False))
        .values(has_voted=True)
        .returning(Voter.id)
    )
    if marked_voter_id is None:
        await get_or_raise(session, Voter, data.voter_id)
        raise ConflictError("Voter has already voted")

    counted_candidate_id = await session.scalar(
        update(Candidate)
        .where(Candidate.id == data.candidate_id)
        .values(votes=Candidate.votes + 1)
        .returning(Candidate.id)
    )
    if counted_candidate_id is None:
        raise NotFoundError.for_entity(Candidate.__name__, data.candidate_id)

    vote = Vote(voter_id=data.voter_id, candidate_id=data.candidate_id)
    session.add(vote)
    await session.commit()
    return vote


async def list_votes(session: AsyncSession, params: PageParams) -> PageResult[Vote]:
    return await paginate(session, select(Vote).order_by(Vote.id), params)


async def get_statistics(session: AsyncSession) -> VotingStatistics:
    await session.connection(execution_options={"isolation_level": "REPEATABLE READ"})

    candidates = (
        await session.scalars(select(Candidate).order_by(Candidate.votes.desc(), Candidate.name))
    ).all()
    total_voters, voters_who_voted = (
        await session.execute(
            select(func.count(Voter.id), func.count(Voter.id).filter(Voter.has_voted))
        )
    ).one()
    total_votes = sum(candidate.votes for candidate in candidates)

    return VotingStatistics(
        total_votes=total_votes,
        voters_who_voted=voters_who_voted,
        total_voters=total_voters,
        turnout_percentage=_percentage(voters_who_voted, total_voters),
        results=[
            CandidateResult(
                candidate_id=candidate.id,
                name=candidate.name,
                party=candidate.party,
                votes=candidate.votes,
                percentage=_percentage(candidate.votes, total_votes),
            )
            for candidate in candidates
        ],
    )


def _percentage(part: int, whole: int) -> float:
    if whole == 0:
        return 0.0
    return round(part * 100 / whole, 2)
