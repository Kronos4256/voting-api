from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str


class DomainError(Exception):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


class NotFoundError(DomainError):
    status_code = status.HTTP_404_NOT_FOUND

    @classmethod
    def for_entity(cls, entity: str, entity_id: int) -> "NotFoundError":
        return cls(f"{entity} {entity_id} not found")


class ConflictError(DomainError):
    status_code = status.HTTP_409_CONFLICT


def error_responses(*status_codes: int) -> dict[int | str, dict]:
    return {code: {"model": ErrorResponse} for code in status_codes}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def handle_domain_error(_: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
