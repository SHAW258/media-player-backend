from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.schemas.category import CategoryResponse

class PodcastEpisodeBase(BaseModel):
    title: str
    description: Optional[str] = None
    duration_seconds: int = 0
    audio_url: str
    cover_url: Optional[str] = None
    episode_number: int = 1

class PodcastEpisodeCreate(PodcastEpisodeBase):
    show_id: int

class PodcastEpisodeResponse(PodcastEpisodeBase):
    id: int
    show_id: int
    published_at: datetime
    stream_count: int = 0
    created_at: datetime
    show_title: Optional[str] = None
    host_name: Optional[str] = None
    is_favorited: Optional[bool] = False

    class Config:
        from_attributes = True

class PodcastShowBase(BaseModel):
    title: str
    host_name: str
    description: Optional[str] = None
    cover_url: Optional[str] = None
    category_id: Optional[int] = None
    rating: float = 5.0

class PodcastShowCreate(PodcastShowBase):
    pass

class PodcastShowResponse(PodcastShowBase):
    id: int
    total_episodes: int = 0
    created_at: datetime
    category: Optional[CategoryResponse] = None
    episodes: Optional[List[PodcastEpisodeResponse]] = []

    class Config:
        from_attributes = True
