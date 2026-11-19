from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, Response, status

from app.api.dependencies import SessionDep
from app.core.errors import error_responses
from app.core.security import require_admin
from app.models import Voter
from app.schemas.common import Page
from app.schemas.voter import VoterCreate, VoterQuery, VoterRead
from app.services import voters
from app.services.queries import PageResult

router = APIRouter(
    prefix="/voters",
    tags=["Voters"],
    dependencies=[Depends(require_admin)],
    responses=error_responses(401),
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=VoterRead,
    responses=error_responses(409),
)
async def register_voter(
    payload: VoterCreate, session: SessionDep, request: Request, response: Response
) -> Voter:
    voter = await voters.register_voter(session, payload)
    response.headers["Location"] = str(request.url_for("get_voter", voter_id=voter.id))
    return voter


@router.get("", response_model=Page[VoterRead])
async def list_voters(
    query: Annotated[VoterQuery, Query()], session: SessionDep
) -> PageResult[Voter]:
    return await voters.list_voters(session, query)


@router.get("/{voter_id}", response_model=VoterRead, responses=error_responses(404))
async def get_voter(voter_id: int, session: SessionDep) -> Voter:
    return await voters.get_voter(session, voter_id)


@router.delete(
    "/{voter_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=error_responses(404, 409),
)
async def delete_voter(voter_id: int, session: SessionDep) -> None:
    await voters.delete_voter(session, voter_id)
