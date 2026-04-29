from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core import security
from app.database import get_db
from app.models.user import User
from app.schemas.user import User as UserSchema, UserUpdate

router = APIRouter()

@router.get("/", response_model=list[UserSchema])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")
    stmt = select(User).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/me", response_model=UserSchema)
async def read_user_me(
    current_user: User = Depends(deps.get_current_user)
):
    return current_user


@router.get("/{user_id}", response_model=UserSchema)
async def read_user_by_id(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    if user_id == current_user.id:
        return current_user
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")
    
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: UUID,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")
    
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data:
        hashed_password = security.get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password
        
    for field, value in update_data.items():
        setattr(user, field, value)
        
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")
        
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    await db.delete(user)
    await db.commit()
