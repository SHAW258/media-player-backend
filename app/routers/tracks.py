import os
import shutil
import uuid
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File, Form, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.track import Track
from app.models.artist import Artist
from app.models.favorite import Favorite
from app.schemas.track import TrackResponse, TrackCreate, TrackUpdate
from app.services.streaming_service import create_streaming_response
from app.config import settings, BASE_DIR
from app.routers.auth import get_current_user, get_current_user_optional
from app.models.user import User

router = APIRouter(prefix="/tracks", tags=["Tracks"])

@router.get("", response_model=List[TrackResponse], summary="List all tracks with filtering")
def list_tracks(
    category_id: Optional[int] = None,
    artist_id: Optional[int] = None,
    album_id: Optional[int] = None,
    media_type: Optional[str] = Query(None, pattern="^(music|podcast)$"),
    skip: int = 0,
    limit: int = 50,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    query = db.query(Track)
    if category_id:
        query = query.filter(Track.category_id == category_id)
    if artist_id:
        query = query.filter(Track.artist_id == artist_id)
    if album_id:
        query = query.filter(Track.album_id == album_id)
    if media_type:
        query = query.filter(Track.media_type == media_type)
    
    tracks = query.offset(skip).limit(limit).all()

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

@router.get("/{track_id}", response_model=TrackResponse, summary="Get single track details")
def get_track(
    track_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    
    res = TrackResponse.model_validate(track)
    if current_user:
        fav = db.query(Favorite).filter(Favorite.user_id == current_user.id, Favorite.track_id == track.id).first()
        res.is_favorited = fav is not None
    return res

@router.get("/{track_id}/lyrics", summary="Get lyrics for a track")
def get_track_lyrics(track_id: int, db: Session = Depends(get_db)):
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    return {
        "track_id": track.id,
        "title": track.title,
        "artist": track.artist.name if track.artist else "Unknown Artist",
        "lyrics": track.lyrics or "Lyrics not available for this track."
    }

@router.get("/{track_id}/stream", summary="Stream track audio with HTTP 206 Range seeking support")
def stream_track_audio(
    track_id: int,
    range: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Streams the audio file for media player playback.
    Supports HTTP Range headers for scrubbing/seeking on mobile and web player UI.
    Increments stream count on successful play start.
    """
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    
    # Check if local file exists or is remote URL
    audio_path = None
    if track.audio_url.startswith("/static/") or track.audio_url.startswith("/uploads/"):
        relative_path = track.audio_url.lstrip("/")
        audio_path = BASE_DIR / relative_path
    elif Path(track.audio_url).exists():
        audio_path = Path(track.audio_url)
    else:
        # Check static directory default
        audio_path = settings.STATIC_DIR / "audio" / Path(track.audio_url).name

    # Increment stream count when starting from range 0 or full request
    if not range or "bytes=0-" in range:
        track.stream_count += 1
        db.commit()

    if audio_path and audio_path.exists():
        return create_streaming_response(audio_path, range_header=range)
    
    # If audio file is a remote URL link or sample placeholder, redirect
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=track.audio_url)

@router.post("", response_model=TrackResponse, status_code=status.HTTP_201_CREATED, summary="Create a new track metadata")
def create_track(
    track_in: TrackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    artist = db.query(Artist).filter(Artist.id == track_in.artist_id).first()
    if not artist:
        raise HTTPException(status_code=400, detail="Artist not found")
    
    track = Track(**track_in.model_dump())
    db.add(track)
    db.commit()
    db.refresh(track)
    return TrackResponse.model_validate(track)

@router.post("/upload", response_model=TrackResponse, status_code=status.HTTP_201_CREATED, summary="Upload audio file and create track")
def upload_track(
    title: str = Form(...),
    artist_id: int = Form(...),
    duration_seconds: int = Form(...),
    album_id: Optional[int] = Form(None),
    category_id: Optional[int] = Form(None),
    lyrics: Optional[str] = Form(None),
    is_trending: bool = Form(False),
    audio_file: UploadFile = File(...),
    cover_file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=400, detail="Artist not found")

    # Save audio file
    audio_ext = Path(audio_file.filename).suffix or ".mp3"
    audio_filename = f"{uuid.uuid4()}{audio_ext}"
    audio_save_path = settings.UPLOAD_DIR / "audio" / audio_filename
    with open(audio_save_path, "wb") as f:
        shutil.copyfileobj(audio_file.file, f)
    
    audio_url = f"/uploads/audio/{audio_filename}"

    # Save cover image if provided
    cover_url = "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=500"
    if cover_file:
        cover_ext = Path(cover_file.filename).suffix or ".jpg"
        cover_filename = f"{uuid.uuid4()}{cover_ext}"
        cover_save_path = settings.UPLOAD_DIR / "covers" / cover_filename
        with open(cover_save_path, "wb") as f:
            shutil.copyfileobj(cover_file.file, f)
        cover_url = f"/uploads/covers/{cover_filename}"

    track = Track(
        title=title,
        artist_id=artist_id,
        album_id=album_id,
        category_id=category_id,
        duration_seconds=duration_seconds,
        audio_url=audio_url,
        cover_url=cover_url,
        lyrics=lyrics,
        is_trending=is_trending,
        media_type="music"
    )
    db.add(track)
    db.commit()
    db.refresh(track)
    return TrackResponse.model_validate(track)

@router.delete("/{track_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a track")
def delete_track(
    track_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    db.delete(track)
    db.commit()
    return None
