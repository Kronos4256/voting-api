from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.common import Email, Name, PageParams


class VoterCreate(BaseModel):
    name: Name
    email: Email


class VoterRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    has_voted: bool
    created_at: datetime


class VoterQuery(PageParams):
    name: str | None = None
    has_voted: bool | None = None
