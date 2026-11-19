from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.common import Email, Name, PageParams


class CandidateCreate(BaseModel):
    name: Name
    email: Email
    party: Name | None = None


class CandidateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    party: str | None
    votes: int
    created_at: datetime


class CandidateQuery(PageParams):
    name: str | None = None
    party: str | None = None
