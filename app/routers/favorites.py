from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.favorite import Favorite
from app.models.track import Track
from app.models.album import Album
from app.models.podcast import PodcastEpisode
from app.schemas.favorite import FavoriteToggleRequest, FavoriteResponse, MyFavoritesResponse
from app.schemas.track import TrackResponse
from app.schemas.album import AlbumResponse
from app.schemas.podcast import PodcastEpisodeResponse
from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/favorites", tags=["Favorites & Likes"])

@router.post("/toggle", summary="Toggle like/favorite on a track, album, or podcast episode")
def toggle_favorite(
    request: FavoriteToggleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Heart button action in Player UI and list rows.
    If item is favorited, removes it; if not favorited, adds it.
    """
    if not request.track_id and not request.podcast_episode_id and not request.album_id:
        raise HTTPException(status_code=400, detail="Must provide track_id, podcast_episode_id, or album_id")

    query = db.query(Favorite).filter(Favorite.user_id == current_user.id)
    if request.track_id:
        query = query.filter(Favorite.track_id == request.track_id)
    elif request.podcast_episode_id:
        query = query.filter(Favorite.podcast_episode_id == request.podcast_episode_id)
    elif request.album_id:
        query = query.filter(Favorite.album_id == request.album_id)

    existing = query.first()
    if existing:
        db.delete(existing)
        db.commit()
        return {"is_favorited": False, "message": "Removed from favorites"}
    else:
        fav = Favorite(
            user_id=current_user.id,
            track_id=request.track_id,
            podcast_episode_id=request.podcast_episode_id,
            album_id=request.album_id
        )
        db.add(fav)
        db.commit()
        db.refresh(fav)
        return {"is_favorited": True, "message": "Added to favorites", "favorite_id": fav.id}

@router.get("/my-favorites", response_model=MyFavoritesResponse, summary="Get all favorited tracks, albums, and podcasts for the current user")
def get_my_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    favs = db.query(Favorite).filter(Favorite.user_id == current_user.id).all()
    
    tracks = []
    albums = []
    podcast_episodes = []

    for f in favs:
        if f.track:
            res = TrackResponse.model_validate(f.track)
            res.is_favorited = True
            tracks.append(res)
        elif f.album:
            albums.append(AlbumResponse.model_validate(f.album))
        elif f.podcast_episode:
            res = PodcastEpisodeResponse.model_validate(f.podcast_episode)
            res.show_title = f.podcast_episode.show.title if f.podcast_episode.show else None
            res.host_name = f.podcast_episode.show.host_name if f.podcast_episode.show else None
            res.is_favorited = True
            podcast_episodes.append(res)

    return MyFavoritesResponse(
        tracks=tracks,
        albums=albums,
        podcast_episodes=podcast_episodes
    )
