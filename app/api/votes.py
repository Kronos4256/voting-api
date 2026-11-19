from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import SessionDep
from app.core.errors import error_responses
from app.core.security import require_admin
from app.models import Vote
from app.schemas.common import Page, PageParams
from app.schemas.vote import VoteCreate, VoteRead, VotingStatistics
from app.services import votes
from app.services.queries import PageResult

router = APIRouter(
    prefix="/votes",
    tags=["Votes"],
    dependencies=[Depends(require_admin)],
    responses=error_responses(401),
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=VoteRead,
    responses=error_responses(404, 409),
)
async def cast_vote(payload: VoteCreate, session: SessionDep) -> Vote:
    return await votes.cast_vote(session, payload)


@router.get("", response_model=Page[VoteRead])
async def list_votes(
    params: Annotated[PageParams, Query()], session: SessionDep
) -> PageResult[Vote]:
    return await votes.list_votes(session, params)


@router.get("/statistics", response_model=VotingStatistics)
async def get_statistics(session: SessionDep) -> VotingStatistics:
    return await votes.get_statistics(session)
