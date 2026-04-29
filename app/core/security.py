from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_token(subject: str | Any, expires_delta: timedelta, token_type: str = "access") -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject), "type": token_type}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_access_token(subject: str | Any, expires_delta: timedelta | None = None) -> str:
    if expires_delta:
        return create_token(subject, expires_delta, "access")
    return create_token(
        subject, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES), "access"
    )


def create_refresh_token(subject: str | Any, expires_delta: timedelta | None = None) -> str:
    if expires_delta:
        return create_token(subject, expires_delta, "refresh")
    return create_token(
        subject, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS), "refresh"
    )

def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
