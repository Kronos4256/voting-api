import secrets
from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import get_settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def credentials_are_valid(username: str, password: str) -> bool:
    settings = get_settings()
    username_ok = secrets.compare_digest(username.encode(), settings.admin_username.encode())
    password_ok = secrets.compare_digest(password.encode(), settings.admin_password.encode())
    return username_ok and password_ok


def create_access_token(subject: str) -> str:
    settings = get_settings()
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": subject, "exp": expires_at}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


async def require_admin(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    return payload["sub"]
