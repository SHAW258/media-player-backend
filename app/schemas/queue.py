from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.schemas.track import TrackResponse
from app.schemas.podcast import PodcastEpisodeResponse

class AddToQueueRequest(BaseModel):
    track_id: Optional[int] = None
    podcast_episode_id: Optional[int] = None
    play_next: bool = False

class ReorderQueueRequest(BaseModel):
    queue_item_ids: List[int]

class QueueItemResponse(BaseModel):
    id: int
    user_id: int
    track_id: Optional[int] = None
    podcast_episode_id: Optional[int] = None
    position: int
    created_at: datetime
    track: Optional[TrackResponse] = None
    podcast_episode: Optional[PodcastEpisodeResponse] = None

    class Config:
        from_attributes = True
