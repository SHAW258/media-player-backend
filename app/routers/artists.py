from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.artist import Artist
from app.models.track import Track
from app.models.album import Album
from app.schemas.artist import ArtistResponse, ArtistCreate
from app.schemas.track import TrackResponse
from app.schemas.album import AlbumResponse
from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/artists", tags=["Artists & Musicians"])

@router.get("", response_model=List[ArtistResponse], summary="List all artists")
def list_artists(
    is_popular: Optional[bool] = None,
    category_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(Artist)
    if is_popular is not None:
        query = query.filter(Artist.is_popular == is_popular)
    if category_id is not None:
        query = query.filter(Artist.category_id == category_id)
    return query.order_by(Artist.monthly_listeners.desc()).offset(skip).limit(limit).all()

@router.get("/popular", response_model=List[ArtistResponse], summary="Get popular musicians carousel (Figma Popular Musicians)")
def get_popular_artists(limit: int = 10, db: Session = Depends(get_db)):
    artists = db.query(Artist).filter(Artist.is_popular == True).limit(limit).all()
    if not artists:
        artists = db.query(Artist).order_by(Artist.monthly_listeners.desc()).limit(limit).all()
    return artists

@router.get("/{artist_id}", response_model=ArtistResponse, summary="Get single artist details")
def get_artist(artist_id: int, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    return artist

@router.get("/{artist_id}/top-tracks", response_model=List[TrackResponse], summary="Get top tracks for an artist")
def get_artist_top_tracks(artist_id: int, limit: int = 10, db: Session = Depends(get_db)):
    tracks = db.query(Track).filter(Track.artist_id == artist_id).order_by(Track.stream_count.desc()).limit(limit).all()
    return [TrackResponse.model_validate(t) for t in tracks]

@router.get("/{artist_id}/albums", response_model=List[AlbumResponse], summary="Get albums for an artist")
def get_artist_albums(artist_id: int, db: Session = Depends(get_db)):
    albums = db.query(Album).filter(Album.artist_id == artist_id).order_by(Album.release_date.desc()).all()
    return [AlbumResponse.model_validate(a) for a in albums]

@router.post("", response_model=ArtistResponse, status_code=status.HTTP_201_CREATED, summary="Create a new artist")
def create_artist(
    artist_in: ArtistCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    artist = Artist(**artist_in.model_dump())
    db.add(artist)
    db.commit()
    db.refresh(artist)
    return artist
