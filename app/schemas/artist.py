from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.schemas.category import CategoryResponse

class ArtistBase(BaseModel):
    name: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    header_url: Optional[str] = None
    monthly_listeners: int = 0
    is_verified: bool = False
    is_popular: bool = False
    category_id: Optional[int] = None

class ArtistCreate(ArtistBase):
    pass

class ArtistResponse(ArtistBase):
    id: int
    created_at: datetime
    category: Optional[CategoryResponse] = None

    class Config:
        from_attributes = True

class ArtistSimpleResponse(BaseModel):
    id: int
    name: str
    avatar_url: Optional[str] = None
    monthly_listeners: int = 0
    is_verified: bool = False
    is_popular: bool = False

    class Config:
        from_attributes = True
