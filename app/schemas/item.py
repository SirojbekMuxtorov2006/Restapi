from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ItemBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    is_public: bool = False


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    is_public: bool | None = None


class ItemInDBBase(ItemBase):
    id: UUID
    owner_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Item(ItemInDBBase):
    pass
