from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.queue import UserQueue
from app.models.track import Track
from app.models.podcast import PodcastEpisode
from app.schemas.queue import QueueItemResponse, AddToQueueRequest, ReorderQueueRequest
from app.schemas.track import TrackResponse
from app.schemas.podcast import PodcastEpisodeResponse
from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/queue", tags=["Play Queue"])

@router.get("", response_model=List[QueueItemResponse], summary="Get current user play queue (Up Next)")
def get_user_queue(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    items = db.query(UserQueue).filter(
        UserQueue.user_id == current_user.id
    ).order_by(UserQueue.position.asc()).all()

    result = []
    for item in items:
        res = QueueItemResponse.model_validate(item)
        if item.track:
            res.track = TrackResponse.model_validate(item.track)
        if item.podcast_episode:
            res.podcast_episode = PodcastEpisodeResponse.model_validate(item.podcast_episode)
        result.append(res)
    return result

@router.post("/add", response_model=QueueItemResponse, status_code=status.HTTP_201_CREATED, summary="Add track or podcast episode to queue")
def add_to_queue(
    request: AddToQueueRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not request.track_id and not request.podcast_episode_id:
        raise HTTPException(status_code=400, detail="Must supply track_id or podcast_episode_id")

    # Get max position
    existing_items = db.query(UserQueue).filter(UserQueue.user_id == current_user.id).order_by(UserQueue.position.asc()).all()
    
    if request.play_next and existing_items:
        # Shift all items +1
        for item in existing_items:
            item.position += 1
        new_pos = 0
    else:
        new_pos = len(existing_items)

    queue_item = UserQueue(
        user_id=current_user.id,
        track_id=request.track_id,
        podcast_episode_id=request.podcast_episode_id,
        position=new_pos
    )
    db.add(queue_item)
    db.commit()
    db.refresh(queue_item)

    res = QueueItemResponse.model_validate(queue_item)
    if queue_item.track:
        res.track = TrackResponse.model_validate(queue_item.track)
    if queue_item.podcast_episode:
        res.podcast_episode = PodcastEpisodeResponse.model_validate(queue_item.podcast_episode)
    return res

@router.delete("/{queue_item_id}", status_code=status.HTTP_200_OK, summary="Remove item from queue")
def remove_from_queue(
    queue_item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(UserQueue).filter(
        UserQueue.id == queue_item_id,
        UserQueue.user_id == current_user.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Queue item not found")

    db.delete(item)
    db.commit()
    return {"message": "Queue item removed"}

@router.delete("", status_code=status.HTTP_204_NO_CONTENT, summary="Clear user entire queue")
def clear_queue(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db.query(UserQueue).filter(UserQueue.user_id == current_user.id).delete()
    db.commit()
    return None
