from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.explore import router as explore_router
from app.routers.tracks import router as tracks_router
from app.routers.artists import router as artists_router
from app.routers.albums import router as albums_router
from app.routers.podcasts import router as podcasts_router
from app.routers.playlists import router as playlists_router
from app.routers.favorites import router as favorites_router
from app.routers.playback import router as playback_router
from app.routers.queue import router as queue_router
from app.routers.search import router as search_router

__all__ = [
    "auth_router",
    "users_router",
    "explore_router",
    "tracks_router",
    "artists_router",
    "albums_router",
    "podcasts_router",
    "playlists_router",
    "favorites_router",
    "playback_router",
    "queue_router",
    "search_router",
]
