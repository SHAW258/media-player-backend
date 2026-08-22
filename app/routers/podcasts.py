from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.podcast import PodcastShow, PodcastEpisode
from app.models.favorite import Favorite
from app.schemas.podcast import (
    PodcastShowResponse, PodcastShowCreate,
    PodcastEpisodeResponse, PodcastEpisodeCreate
)
from app.services.streaming_service import create_streaming_response
from app.config import settings, BASE_DIR
from app.routers.auth import get_current_user, get_current_user_optional
from app.models.user import User

router = APIRouter(prefix="/podcasts", tags=["Podcasts & Episodes"])

@router.get("/shows", response_model=List[PodcastShowResponse], summary="List podcast shows")
def list_podcast_shows(
    category_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(PodcastShow)
    if category_id:
        query = query.filter(PodcastShow.category_id == category_id)
    return query.offset(skip).limit(limit).all()

@router.get("/shows/{show_id}", response_model=PodcastShowResponse, summary="Get podcast show details with episodes")
def get_podcast_show(show_id: int, db: Session = Depends(get_db)):
    show = db.query(PodcastShow).filter(PodcastShow.id == show_id).first()
    if not show:
        raise HTTPException(status_code=404, detail="Podcast show not found")
    return show

@router.post("/shows", response_model=PodcastShowResponse, status_code=status.HTTP_201_CREATED, summary="Create a podcast show")
def create_podcast_show(
    show_in: PodcastShowCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    show = PodcastShow(**show_in.model_dump())
    db.add(show)
    db.commit()
    db.refresh(show)
    return show

@router.get("/episodes", response_model=List[PodcastEpisodeResponse], summary="List podcast episodes")
def list_podcast_episodes(
    show_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    query = db.query(PodcastEpisode)
    if show_id:
        query = query.filter(PodcastEpisode.show_id == show_id)
    
    episodes = query.order_by(PodcastEpisode.published_at.desc()).offset(skip).limit(limit).all()
    user_favs = set()
    if current_user:
        favs = db.query(Favorite.podcast_episode_id).filter(Favorite.user_id == current_user.id).all()
        user_favs = {r[0] for r in favs}

    result = []
    for ep in episodes:
        res = PodcastEpisodeResponse.model_validate(ep)
        res.show_title = ep.show.title if ep.show else None
        res.host_name = ep.show.host_name if ep.show else None
        res.is_favorited = ep.id in user_favs
        result.append(res)
    return result

@router.get("/episodes/{episode_id}", response_model=PodcastEpisodeResponse, summary="Get single podcast episode")
def get_podcast_episode(
    episode_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    ep = db.query(PodcastEpisode).filter(PodcastEpisode.id == episode_id).first()
    if not ep:
        raise HTTPException(status_code=404, detail="Podcast episode not found")
    
    res = PodcastEpisodeResponse.model_validate(ep)
    res.show_title = ep.show.title if ep.show else None
    res.host_name = ep.show.host_name if ep.show else None
    if current_user:
        fav = db.query(Favorite).filter(Favorite.user_id == current_user.id, Favorite.podcast_episode_id == ep.id).first()
        res.is_favorited = fav is not None
    return res

@router.get("/episodes/{episode_id}/stream", summary="Stream podcast episode audio with range seeking support")
def stream_podcast_episode(
    episode_id: int,
    range: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    ep = db.query(PodcastEpisode).filter(PodcastEpisode.id == episode_id).first()
    if not ep:
        raise HTTPException(status_code=404, detail="Podcast episode not found")
    
    # Check if local file exists
    audio_path = None
    if ep.audio_url.startswith("/static/") or ep.audio_url.startswith("/uploads/"):
        relative_path = ep.audio_url.lstrip("/")
        audio_path = BASE_DIR / relative_path
    elif Path(ep.audio_url).exists():
        audio_path = Path(ep.audio_url)
    else:
        audio_path = settings.STATIC_DIR / "audio" / Path(ep.audio_url).name

    # Increment stream count on start
    if not range or "bytes=0-" in range:
        ep.stream_count += 1
        db.commit()

    if audio_path and audio_path.exists():
        return create_streaming_response(audio_path, range_header=range)
    
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=ep.audio_url)

@router.post("/episodes", response_model=PodcastEpisodeResponse, status_code=status.HTTP_201_CREATED, summary="Create a podcast episode")
def create_podcast_episode(
    episode_in: PodcastEpisodeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    show = db.query(PodcastShow).filter(PodcastShow.id == episode_in.show_id).first()
    if not show:
        raise HTTPException(status_code=400, detail="Podcast show not found")
    
    ep = PodcastEpisode(**episode_in.model_dump())
    db.add(ep)
    show.total_episodes += 1
    db.commit()
    db.refresh(ep)
    
    res = PodcastEpisodeResponse.model_validate(ep)
    res.show_title = show.title
    res.host_name = show.host_name
    return res
