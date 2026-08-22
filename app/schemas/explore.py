from typing import Optional, List
from pydantic import BaseModel
from app.schemas.track import TrackResponse
from app.schemas.artist import ArtistResponse
from app.schemas.album import AlbumResponse
from app.schemas.podcast import PodcastShowResponse, PodcastEpisodeResponse
from app.schemas.category import CategoryResponse

class HeroBanner(BaseModel):
    id: int
    title: str
    subtitle: str
    image_url: str
    target_type: str  # 'track', 'album', 'artist', 'podcast'
    target_id: int

class HomeFeedResponse(BaseModel):
    tab: str  # 'all', 'music', 'podcast'
    hero: Optional[HeroBanner] = None
    trending_now: List[TrackResponse] = []
    popular_musicians: List[ArtistResponse] = []
    new_releases: List[AlbumResponse] = []
    podcast_shows: List[PodcastShowResponse] = []
    podcast_episodes: List[PodcastEpisodeResponse] = []
    categories: List[CategoryResponse] = []

class SearchResultResponse(BaseModel):
    query: str
    tracks: List[TrackResponse] = []
    artists: List[ArtistResponse] = []
    albums: List[AlbumResponse] = []
    podcast_shows: List[PodcastShowResponse] = []
    podcast_episodes: List[PodcastEpisodeResponse] = []
