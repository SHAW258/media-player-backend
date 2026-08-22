from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.track import Track
from app.models.artist import Artist
from app.models.album import Album
from app.models.podcast import PodcastShow, PodcastEpisode
from app.schemas.explore import SearchResultResponse
from app.schemas.track import TrackResponse
from app.schemas.artist import ArtistResponse
from app.schemas.album import AlbumResponse
from app.schemas.podcast import PodcastShowResponse, PodcastEpisodeResponse

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("", response_model=SearchResultResponse, summary="Universal search across music, artists, albums, and podcasts")
def search_all(
    q: str = Query(..., min_length=1, description="Search keyword"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    keyword = f"%{q}%"

    tracks_db = db.query(Track).filter(Track.title.ilike(keyword)).limit(limit).all()
    artists_db = db.query(Artist).filter(Artist.name.ilike(keyword)).limit(limit).all()
    albums_db = db.query(Album).filter(Album.title.ilike(keyword)).limit(limit).all()
    shows_db = db.query(PodcastShow).filter(
        (PodcastShow.title.ilike(keyword)) | (PodcastShow.host_name.ilike(keyword))
    ).limit(limit).all()
    episodes_db = db.query(PodcastEpisode).filter(PodcastEpisode.title.ilike(keyword)).limit(limit).all()

    tracks = [TrackResponse.model_validate(t) for t in tracks_db]
    artists = [ArtistResponse.model_validate(a) for a in artists_db]
    albums = [AlbumResponse.model_validate(alb) for alb in albums_db]
    shows = [PodcastShowResponse.model_validate(s) for s in shows_db]
    
    episodes = []
    for ep in episodes_db:
        ep_res = PodcastEpisodeResponse.model_validate(ep)
        ep_res.show_title = ep.show.title if ep.show else None
        ep_res.host_name = ep.show.host_name if ep.show else None
        episodes.append(ep_res)

    return SearchResultResponse(
        query=q,
        tracks=tracks,
        artists=artists,
        albums=albums,
        podcast_shows=shows,
        podcast_episodes=episodes
    )
