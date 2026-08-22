from app.schemas.auth import Token, TokenData, LoginRequest, RegisterRequest
from app.schemas.user import UserBase, UserCreate, UserUpdate, UserResponse
from app.schemas.category import CategoryBase, CategoryCreate, CategoryResponse
from app.schemas.artist import ArtistBase, ArtistCreate, ArtistResponse, ArtistSimpleResponse
from app.schemas.album import AlbumBase, AlbumCreate, AlbumResponse, AlbumSimpleResponse
from app.schemas.track import TrackBase, TrackCreate, TrackUpdate, TrackResponse, TrackSimpleResponse
from app.schemas.podcast import (
    PodcastEpisodeBase, PodcastEpisodeCreate, PodcastEpisodeResponse,
    PodcastShowBase, PodcastShowCreate, PodcastShowResponse
)
from app.schemas.playlist import (
    PlaylistBase, PlaylistCreate, PlaylistUpdate,
    PlaylistTrackResponse, PlaylistResponse, PlaylistDetailResponse, AddTrackToPlaylistRequest
)
from app.schemas.favorite import FavoriteToggleRequest, FavoriteResponse, MyFavoritesResponse
from app.schemas.history import PlaybackProgressUpdate, PlaybackHistoryResponse
from app.schemas.queue import AddToQueueRequest, ReorderQueueRequest, QueueItemResponse
from app.schemas.explore import HeroBanner, HomeFeedResponse, SearchResultResponse

__all__ = [
    "Token", "TokenData", "LoginRequest", "RegisterRequest",
    "UserBase", "UserCreate", "UserUpdate", "UserResponse",
    "CategoryBase", "CategoryCreate", "CategoryResponse",
    "ArtistBase", "ArtistCreate", "ArtistResponse", "ArtistSimpleResponse",
    "AlbumBase", "AlbumCreate", "AlbumResponse", "AlbumSimpleResponse",
    "TrackBase", "TrackCreate", "TrackUpdate", "TrackResponse", "TrackSimpleResponse",
    "PodcastEpisodeBase", "PodcastEpisodeCreate", "PodcastEpisodeResponse",
    "PodcastShowBase", "PodcastShowCreate", "PodcastShowResponse",
    "PlaylistBase", "PlaylistCreate", "PlaylistUpdate",
    "PlaylistTrackResponse", "PlaylistResponse", "PlaylistDetailResponse", "AddTrackToPlaylistRequest",
    "FavoriteToggleRequest", "FavoriteResponse", "MyFavoritesResponse",
    "PlaybackProgressUpdate", "PlaybackHistoryResponse",
    "AddToQueueRequest", "ReorderQueueRequest", "QueueItemResponse",
    "HeroBanner", "HomeFeedResponse", "SearchResultResponse",
]
