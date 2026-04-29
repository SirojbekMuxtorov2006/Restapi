from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core import security
from app.database import get_db
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import User as UserSchema, UserCreate

router = APIRouter()

@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    # Check if user exists
    stmt = select(User).where((User.email == user_in.email) | (User.username == user_in.username))
    result = await db.execute(stmt)
    if result.scalars().first():
        raise HTTPException(
            status_code=400,
            detail="The user with this username or email already exists in the system."
        )

    user = User(
        email=user_in.email,
        username=user_in.username,
        full_name=user_in.full_name,
        hashed_password=security.get_password_hash(user_in.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=Token)
async def login(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    # Authenticate
    stmt = select(User).where(User.username == form_data.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # Generate tokens
    access_token = security.create_access_token(user.id)
    refresh_token = security.create_refresh_token(user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user: User = Depends(deps.get_current_user)
):
    # For a real implementation, you'd likely expect the refresh token itself to be passed.
    # To keep it simple, if they can authenticate with an unexpired access token, we can give a new pair.
    # Or, normally you'd parse a separate refresh token from a cookie or body.
    
    # In this minimal demo: if the user object is valid, generate new tokens.
    access_token = security.create_access_token(current_user.id)
    refresh_token = security.create_refresh_token(current_user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
