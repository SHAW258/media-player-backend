from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.track import Track
from app.models.artist import Artist
from app.models.album import Album
from app.models.podcast import PodcastShow, PodcastEpisode
from app.models.category import Category
from app.models.favorite import Favorite
from app.schemas.explore import HomeFeedResponse, HeroBanner
from app.schemas.track import TrackResponse
from app.schemas.artist import ArtistResponse
from app.schemas.album import AlbumResponse
from app.schemas.podcast import PodcastShowResponse, PodcastEpisodeResponse
from app.schemas.category import CategoryResponse
from app.routers.auth import get_current_user_optional
from app.models.user import User

router = APIRouter(prefix="/explore", tags=["Explore & Feeds"])

@router.get("/home", response_model=HomeFeedResponse, summary="Get full home feed (matching Figma screen tabs)")
def get_home_feed(
    tab: str = Query("all", pattern="^(all|music|podcast)$", description="Filter tab: 'all', 'music', or 'podcast'"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Returns aggregated home screen data customized for the active tab (All, Music, Podcast)
    including Trending tracks, Popular musicians, New Releases, and Podcasts as shown in Figma.
    """
    user_favorites_track_ids = set()
    user_favorites_episode_ids = set()
    if current_user:
        fav_tracks = db.query(Favorite.track_id).filter(Favorite.user_id == current_user.id, Favorite.track_id.isnot(None)).all()
        fav_eps = db.query(Favorite.podcast_episode_id).filter(Favorite.user_id == current_user.id, Favorite.podcast_episode_id.isnot(None)).all()
        user_favorites_track_ids = {r[0] for r in fav_tracks}
        user_favorites_episode_ids = {r[0] for r in fav_eps}

    # 1. Categories
    category_type_filter = ["both"]
    if tab == "music":
        category_type_filter.append("music")
    elif tab == "podcast":
        category_type_filter.append("podcast")
    else:
        category_type_filter.extend(["music", "podcast"])
    
    categories = db.query(Category).filter(Category.category_type.in_(category_type_filter)).all()

    # 2. Trending tracks
    trending_query = db.query(Track)
    if tab == "music":
        trending_query = trending_query.filter(Track.media_type == "music")
    elif tab == "podcast":
        trending_query = trending_query.filter(Track.media_type == "podcast")
    
    trending_tracks_db = trending_query.filter(Track.is_trending == True).limit(10).all()
    if not trending_tracks_db:
        trending_tracks_db = trending_query.order_by(Track.stream_count.desc()).limit(10).all()

    trending_now = []
    for t in trending_tracks_db:
        t_res = TrackResponse.model_validate(t)
        t_res.is_favorited = t.id in user_favorites_track_ids
        trending_now.append(t_res)

    # 3. Popular musicians / Artists
    popular_artists_db = db.query(Artist).filter(Artist.is_popular == True).limit(10).all()
    if not popular_artists_db:
        popular_artists_db = db.query(Artist).order_by(Artist.monthly_listeners.desc()).limit(10).all()
    popular_musicians = [ArtistResponse.model_validate(a) for a in popular_artists_db]

    # 4. New Releases (Albums & Singles)
    new_releases_db = db.query(Album).filter(Album.is_new_release == True).limit(10).all()
    if not new_releases_db:
        new_releases_db = db.query(Album).order_by(Album.release_date.desc()).limit(10).all()
    new_releases = [AlbumResponse.model_validate(alb) for alb in new_releases_db]

    # 5. Podcast Shows & Episodes
    podcast_shows = []
    podcast_episodes = []
    if tab in ("all", "podcast"):
        shows_db = db.query(PodcastShow).limit(8).all()
        podcast_shows = [PodcastShowResponse.model_validate(s) for s in shows_db]

        episodes_db = db.query(PodcastEpisode).order_by(PodcastEpisode.published_at.desc()).limit(8).all()
        for ep in episodes_db:
            ep_res = PodcastEpisodeResponse.model_validate(ep)
            ep_res.show_title = ep.show.title if ep.show else None
            ep_res.host_name = ep.show.host_name if ep.show else None
            ep_res.is_favorited = ep.id in user_favorites_episode_ids
            podcast_episodes.append(ep_res)

    # 6. Hero Banner (e.g. Featured Track 'Ghost' or featured podcast)
    hero = None
    if tab == "podcast" and podcast_shows:
        hero = HeroBanner(
            id=podcast_shows[0].id,
            title=podcast_shows[0].title,
            subtitle=f"Hosted by {podcast_shows[0].host_name}",
            image_url=podcast_shows[0].cover_url or "https://images.unsplash.com/photo-1590602847861-f357a9332bbc?w=800",
            target_type="podcast",
            target_id=podcast_shows[0].id
        )
    elif trending_now:
        hero = HeroBanner(
            id=trending_now[0].id,
            title=trending_now[0].title,
            subtitle=trending_now[0].artist.name if trending_now[0].artist else "Featured Artist",
            image_url=trending_now[0].cover_url or "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=800",
            target_type="track",
            target_id=trending_now[0].id
        )

    return HomeFeedResponse(
        tab=tab,
        hero=hero,
        trending_now=trending_now,
        popular_musicians=popular_musicians,
        new_releases=new_releases,
        podcast_shows=podcast_shows,
        podcast_episodes=podcast_episodes,
        categories=[CategoryResponse.model_validate(c) for c in categories]
    )

@router.get("/trending", response_model=List[TrackResponse], summary="Get list of trending tracks")
def get_trending_tracks(
    media_type: Optional[str] = Query(None, pattern="^(music|podcast)$"),
    limit: int = 20,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    query = db.query(Track).filter(Track.is_trending == True)
    if media_type:
        query = query.filter(Track.media_type == media_type)
    
    tracks = query.order_by(Track.stream_count.desc()).limit(limit).all()
    user_favs = set()
    if current_user:
        favs = db.query(Favorite.track_id).filter(Favorite.user_id == current_user.id).all()
        user_favs = {r[0] for r in favs}

    result = []
    for t in tracks:
        res = TrackResponse.model_validate(t)
        res.is_favorited = t.id in user_favs
        result.append(res)
    return result

@router.get("/categories", response_model=List[CategoryResponse], summary="Get all music/podcast categories")
def get_categories(category_type: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Category)
    if category_type:
        query = query.filter((Category.category_type == category_type) | (Category.category_type == "both"))
    return query.all()
