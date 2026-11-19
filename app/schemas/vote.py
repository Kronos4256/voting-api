from datetime import datetime

from pydantic import BaseModel, ConfigDict, PositiveInt


class VoteCreate(BaseModel):
    voter_id: PositiveInt
    candidate_id: PositiveInt


class VoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    voter_id: int
    candidate_id: int
    created_at: datetime


class CandidateResult(BaseModel):
    candidate_id: int
    name: str
    party: str | None
    votes: int
    percentage: float


class VotingStatistics(BaseModel):
    total_votes: int
    voters_who_voted: int
    total_voters: int
    turnout_percentage: float
    results: list[CandidateResult]
