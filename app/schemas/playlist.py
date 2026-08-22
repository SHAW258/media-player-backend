from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.schemas.track import TrackResponse

class PlaylistBase(BaseModel):
    name: str
    description: Optional[str] = None
    cover_url: Optional[str] = None
    is_public: bool = True

class PlaylistCreate(PlaylistBase):
    pass

class PlaylistUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    cover_url: Optional[str] = None
    is_public: Optional[bool] = None

class PlaylistTrackResponse(BaseModel):
    id: int
    track_id: int
    position: int
    added_at: datetime
    track: Optional[TrackResponse] = None

    class Config:
        from_attributes = True

class PlaylistResponse(PlaylistBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    track_count: Optional[int] = 0

    class Config:
        from_attributes = True

class PlaylistDetailResponse(PlaylistResponse):
    tracks: List[PlaylistTrackResponse] = []

class AddTrackToPlaylistRequest(BaseModel):
    track_id: int
    position: Optional[int] = None
