from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.schemas.track import TrackResponse
from app.schemas.album import AlbumResponse
from app.schemas.podcast import PodcastEpisodeResponse

class FavoriteToggleRequest(BaseModel):
    track_id: Optional[int] = None
    podcast_episode_id: Optional[int] = None
    album_id: Optional[int] = None

class FavoriteResponse(BaseModel):
    id: int
    user_id: int
    track_id: Optional[int] = None
    podcast_episode_id: Optional[int] = None
    album_id: Optional[int] = None
    created_at: datetime
    is_favorited: bool = True

    class Config:
        from_attributes = True

class MyFavoritesResponse(BaseModel):
    tracks: List[TrackResponse] = []
    albums: List[AlbumResponse] = []
    podcast_episodes: List[PodcastEpisodeResponse] = []
