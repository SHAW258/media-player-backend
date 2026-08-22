from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class UserQueue(Base):
    __tablename__ = "user_queue"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id", ondelete="CASCADE"), nullable=True)
    podcast_episode_id = Column(Integer, ForeignKey("podcast_episodes.id", ondelete="CASCADE"), nullable=True)
    position = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="queue_items")
    track = relationship("Track", back_populates="queue_items")
    podcast_episode = relationship("PodcastEpisode", back_populates="queue_items")
