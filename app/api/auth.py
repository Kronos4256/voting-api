from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.errors import error_responses
from app.core.security import create_access_token, credentials_are_valid
from app.schemas.auth import Token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/token", response_model=Token, responses=error_responses(401))
async def issue_token(form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    if not credentials_are_valid(form.username, form.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_access_token(form.username))
