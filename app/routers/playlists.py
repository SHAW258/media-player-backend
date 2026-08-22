from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.playlist import Playlist, PlaylistTrack
from app.models.track import Track
from app.schemas.playlist import (
    PlaylistResponse, PlaylistDetailResponse, PlaylistCreate, PlaylistUpdate,
    AddTrackToPlaylistRequest
)
from app.routers.auth import get_current_user, get_current_user_optional
from app.models.user import User

router = APIRouter(prefix="/playlists", tags=["Playlists"])

@router.get("", response_model=List[PlaylistResponse], summary="List public playlists or user playlists")
def list_playlists(
    user_id: Optional[int] = None,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    query = db.query(Playlist)
    if user_id:
        query = query.filter(Playlist.user_id == user_id)
    else:
        # If user is authenticated, return public playlists and user's own playlists
        if current_user:
            query = query.filter((Playlist.is_public == True) | (Playlist.user_id == current_user.id))
        else:
            query = query.filter(Playlist.is_public == True)
    
    playlists = query.all()
    result = []
    for p in playlists:
        res = PlaylistResponse.model_validate(p)
        res.track_count = len(p.tracks)
        result.append(res)
    return result

@router.get("/{playlist_id}", response_model=PlaylistDetailResponse, summary="Get full playlist with all tracks")
def get_playlist_detail(
    playlist_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    if not playlist.is_public and (not current_user or current_user.id != playlist.user_id):
        raise HTTPException(status_code=403, detail="This playlist is private")
    
    res = PlaylistDetailResponse.model_validate(playlist)
    res.track_count = len(playlist.tracks)
    return res

@router.post("", response_model=PlaylistResponse, status_code=status.HTTP_201_CREATED, summary="Create a new playlist")
def create_playlist(
    playlist_in: PlaylistCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    playlist = Playlist(
        user_id=current_user.id,
        name=playlist_in.name,
        description=playlist_in.description,
        cover_url=playlist_in.cover_url or "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=500",
        is_public=playlist_in.is_public
    )
    db.add(playlist)
    db.commit()
    db.refresh(playlist)
    
    res = PlaylistResponse.model_validate(playlist)
    res.track_count = 0
    return res

@router.put("/{playlist_id}", response_model=PlaylistResponse, summary="Update playlist details")
def update_playlist(
    playlist_id: int,
    playlist_in: PlaylistUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if playlist.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this playlist")

    if playlist_in.name is not None:
        playlist.name = playlist_in.name
    if playlist_in.description is not None:
        playlist.description = playlist_in.description
    if playlist_in.cover_url is not None:
        playlist.cover_url = playlist_in.cover_url
    if playlist_in.is_public is not None:
        playlist.is_public = playlist_in.is_public

    db.commit()
    db.refresh(playlist)
    res = PlaylistResponse.model_validate(playlist)
    res.track_count = len(playlist.tracks)
    return res

@router.post("/{playlist_id}/tracks", status_code=status.HTTP_201_CREATED, summary="Add track to playlist")
def add_track_to_playlist(
    playlist_id: int,
    request: AddTrackToPlaylistRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if playlist.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this playlist")

    track = db.query(Track).filter(Track.id == request.track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    existing = db.query(PlaylistTrack).filter(
        PlaylistTrack.playlist_id == playlist_id,
        PlaylistTrack.track_id == request.track_id
    ).first()
    if existing:
        return {"message": "Track already in playlist"}

    pos = request.position if request.position is not None else len(playlist.tracks)
    playlist_track = PlaylistTrack(
        playlist_id=playlist_id,
        track_id=request.track_id,
        position=pos
    )
    db.add(playlist_track)
    db.commit()
    return {"message": "Track added successfully", "playlist_id": playlist_id, "track_id": track.id}

@router.delete("/{playlist_id}/tracks/{track_id}", status_code=status.HTTP_200_OK, summary="Remove track from playlist")
def remove_track_from_playlist(
    playlist_id: int,
    track_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if playlist.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this playlist")

    pt = db.query(PlaylistTrack).filter(
        PlaylistTrack.playlist_id == playlist_id,
        PlaylistTrack.track_id == track_id
    ).first()
    if not pt:
        raise HTTPException(status_code=404, detail="Track not found in playlist")

    db.delete(pt)
    db.commit()
    return {"message": "Track removed from playlist"}

@router.delete("/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete playlist")
def delete_playlist(
    playlist_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if playlist.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this playlist")

    db.delete(playlist)
    db.commit()
    return None
