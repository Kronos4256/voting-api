from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, Response, status

from app.api.dependencies import SessionDep
from app.core.errors import error_responses
from app.core.security import require_admin
from app.models import Candidate
from app.schemas.candidate import CandidateCreate, CandidateQuery, CandidateRead
from app.schemas.common import Page
from app.services import candidates
from app.services.queries import PageResult

router = APIRouter(
    prefix="/candidates",
    tags=["Candidates"],
    dependencies=[Depends(require_admin)],
    responses=error_responses(401),
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=CandidateRead,
    responses=error_responses(409),
)
async def register_candidate(
    payload: CandidateCreate, session: SessionDep, request: Request, response: Response
) -> Candidate:
    candidate = await candidates.register_candidate(session, payload)
    response.headers["Location"] = str(request.url_for("get_candidate", candidate_id=candidate.id))
    return candidate


@router.get("", response_model=Page[CandidateRead])
async def list_candidates(
    query: Annotated[CandidateQuery, Query()], session: SessionDep
) -> PageResult[Candidate]:
    return await candidates.list_candidates(session, query)


@router.get("/{candidate_id}", response_model=CandidateRead, responses=error_responses(404))
async def get_candidate(candidate_id: int, session: SessionDep) -> Candidate:
    return await candidates.get_candidate(session, candidate_id)


@router.delete(
    "/{candidate_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=error_responses(404, 409),
)
async def delete_candidate(candidate_id: int, session: SessionDep) -> None:
    await candidates.delete_candidate(session, candidate_id)
