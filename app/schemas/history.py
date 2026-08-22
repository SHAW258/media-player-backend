from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.schemas.track import TrackResponse
from app.schemas.podcast import PodcastEpisodeResponse

class PlaybackProgressUpdate(BaseModel):
    track_id: Optional[int] = None
    podcast_episode_id: Optional[int] = None
    progress_seconds: int
    completed: bool = False

class PlaybackHistoryResponse(BaseModel):
    id: int
    user_id: int
    track_id: Optional[int] = None
    podcast_episode_id: Optional[int] = None
    progress_seconds: int
    completed: bool
    played_at: datetime
    track: Optional[TrackResponse] = None
    podcast_episode: Optional[PodcastEpisodeResponse] = None

    class Config:
        from_attributes = True
