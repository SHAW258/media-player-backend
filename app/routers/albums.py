from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.album import Album
from app.models.track import Track
from app.schemas.album import AlbumResponse, AlbumCreate
from app.schemas.track import TrackResponse
from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/albums", tags=["Albums & Releases"])

@router.get("", response_model=List[AlbumResponse], summary="List albums")
def list_albums(
    is_new_release: Optional[bool] = None,
    artist_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(Album)
    if is_new_release is not None:
        query = query.filter(Album.is_new_release == is_new_release)
    if artist_id is not None:
        query = query.filter(Album.artist_id == artist_id)
    return query.order_by(Album.release_date.desc()).offset(skip).limit(limit).all()

@router.get("/new-releases", response_model=List[AlbumResponse], summary="Get new releases (Figma New Releases)")
def get_new_releases(limit: int = 10, db: Session = Depends(get_db)):
    albums = db.query(Album).filter(Album.is_new_release == True).limit(limit).all()
    if not albums:
        albums = db.query(Album).order_by(Album.release_date.desc()).limit(limit).all()
    return albums

@router.get("/{album_id}", response_model=AlbumResponse, summary="Get single album details")
def get_album(album_id: int, db: Session = Depends(get_db)):
    album = db.query(Album).filter(Album.id == album_id).first()
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    return album

@router.get("/{album_id}/tracks", response_model=List[TrackResponse], summary="Get all tracks inside an album")
def get_album_tracks(album_id: int, db: Session = Depends(get_db)):
    album = db.query(Album).filter(Album.id == album_id).first()
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    tracks = db.query(Track).filter(Track.album_id == album_id).all()
    return [TrackResponse.model_validate(t) for t in tracks]

@router.post("", response_model=AlbumResponse, status_code=status.HTTP_201_CREATED, summary="Create a new album")
def create_album(
    album_in: AlbumCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    album = Album(**album_in.model_dump())
    db.add(album)
    db.commit()
    db.refresh(album)
    return album
