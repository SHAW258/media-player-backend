from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.schemas.artist import ArtistSimpleResponse
from app.schemas.album import AlbumSimpleResponse
from app.schemas.category import CategoryResponse

class TrackBase(BaseModel):
    title: str
    artist_id: int
    album_id: Optional[int] = None
    category_id: Optional[int] = None
    duration_seconds: int = 0
    audio_url: str
    cover_url: Optional[str] = None
    lyrics: Optional[str] = None
    is_trending: bool = False
    is_new_release: bool = False
    media_type: str = "music"

class TrackCreate(TrackBase):
    pass

class TrackUpdate(BaseModel):
    title: Optional[str] = None
    album_id: Optional[int] = None
    category_id: Optional[int] = None
    duration_seconds: Optional[int] = None
    audio_url: Optional[str] = None
    cover_url: Optional[str] = None
    lyrics: Optional[str] = None
    is_trending: Optional[bool] = None
    is_new_release: Optional[bool] = None

class TrackResponse(TrackBase):
    id: int
    stream_count: int = 0
    created_at: datetime
    artist: Optional[ArtistSimpleResponse] = None
    album: Optional[AlbumSimpleResponse] = None
    is_favorited: Optional[bool] = False

    class Config:
        from_attributes = True

class TrackSimpleResponse(BaseModel):
    id: int
    title: str
    duration_seconds: int
    audio_url: str
    cover_url: Optional[str] = None
    stream_count: int = 0
    is_trending: bool = False
    media_type: str = "music"
    artist_name: Optional[str] = None
    album_title: Optional[str] = None

    class Config:
        from_attributes = True
