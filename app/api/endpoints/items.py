from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.database import get_db
from app.models.item import Item
from app.models.user import User
from app.schemas.item import Item as ItemSchema, ItemCreate, ItemUpdate

router = APIRouter()

@router.post("/", response_model=ItemSchema, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_in: ItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    item = Item(**item_in.model_dump(), owner_id=current_user.id)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.get("/", response_model=list[ItemSchema])
async def read_items(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    stmt = select(Item).where(Item.owner_id == current_user.id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{item_id}", response_model=ItemSchema)
async def read_item(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    item = await db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")
    return item


@router.put("/{item_id}", response_model=ItemSchema)
async def update_item(
    item_id: UUID,
    item_in: ItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    item = await db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")
        
    update_data = item_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
        
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    item = await db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")
        
    await db.delete(item)
    await db.commit()
