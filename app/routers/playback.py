from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.history import PlaybackHistory
from app.models.track import Track
from app.models.podcast import PodcastEpisode
from app.schemas.history import PlaybackProgressUpdate, PlaybackHistoryResponse
from app.schemas.track import TrackResponse
from app.schemas.podcast import PodcastEpisodeResponse
from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/playback", tags=["Playback & History"])

@router.post("/progress", summary="Record or update playback progress (for seeking and resume)")
def update_playback_progress(
    update_in: PlaybackProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Updates the current player position (e.g. 2:34 / 3:45) so user can resume anytime.
    """
    query = db.query(PlaybackHistory).filter(PlaybackHistory.user_id == current_user.id)
    if update_in.track_id:
        query = query.filter(PlaybackHistory.track_id == update_in.track_id)
    elif update_in.podcast_episode_id:
        query = query.filter(PlaybackHistory.podcast_episode_id == update_in.podcast_episode_id)
    else:
        raise HTTPException(status_code=400, detail="Must supply track_id or podcast_episode_id")

    record = query.first()
    if record:
        record.progress_seconds = update_in.progress_seconds
        record.completed = update_in.completed
        record.played_at = datetime.now(timezone.utc)
    else:
        record = PlaybackHistory(
            user_id=current_user.id,
            track_id=update_in.track_id,
            podcast_episode_id=update_in.podcast_episode_id,
            progress_seconds=update_in.progress_seconds,
            completed=update_in.completed,
            played_at=datetime.now(timezone.utc)
        )
        db.add(record)

    db.commit()
    db.refresh(record)
    return {
        "status": "success",
        "progress_seconds": record.progress_seconds,
        "completed": record.completed,
        "played_at": record.played_at
    }

@router.get("/history", response_model=List[PlaybackHistoryResponse], summary="Get user recently played history")
def get_playback_history(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    history_items = db.query(PlaybackHistory).filter(
        PlaybackHistory.user_id == current_user.id
    ).order_by(PlaybackHistory.played_at.desc()).limit(limit).all()

    result = []
    for h in history_items:
        res = PlaybackHistoryResponse.model_validate(h)
        if h.track:
            res.track = TrackResponse.model_validate(h.track)
        if h.podcast_episode:
            res.podcast_episode = PodcastEpisodeResponse.model_validate(h.podcast_episode)
        result.append(res)
    return result

@router.delete("/history", status_code=status.HTTP_204_NO_CONTENT, summary="Clear user listening history")
def clear_playback_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db.query(PlaybackHistory).filter(PlaybackHistory.user_id == current_user.id).delete()
    db.commit()
    return None
