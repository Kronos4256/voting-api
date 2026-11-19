from typing import Annotated

from pydantic import AfterValidator, BaseModel, EmailStr, Field, StringConstraints

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
Email = Annotated[EmailStr, AfterValidator(str.lower)]


class PageParams(BaseModel):
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


class Page[T](BaseModel):
    items: list[T]
    total: int
    page: int
    size: int
