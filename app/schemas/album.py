from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel
from app.schemas.artist import ArtistSimpleResponse

class AlbumBase(BaseModel):
    title: str
    artist_id: int
    cover_url: Optional[str] = None
    release_date: Optional[date] = None
    album_type: str = "album"  # 'album', 'single', 'ep'
    total_tracks: int = 1
    is_new_release: bool = False

class AlbumCreate(AlbumBase):
    pass

class AlbumResponse(AlbumBase):
    id: int
    created_at: datetime
    artist: Optional[ArtistSimpleResponse] = None

    class Config:
        from_attributes = True

class AlbumSimpleResponse(BaseModel):
    id: int
    title: str
    cover_url: Optional[str] = None
    release_date: Optional[date] = None
    album_type: str = "album"
    is_new_release: bool = False

    class Config:
        from_attributes = True
