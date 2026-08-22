from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class PlaybackHistory(Base):
    __tablename__ = "playback_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id", ondelete="SET NULL"), nullable=True)
    podcast_episode_id = Column(Integer, ForeignKey("podcast_episodes.id", ondelete="SET NULL"), nullable=True)
    progress_seconds = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    played_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    user = relationship("User", back_populates="history")
    track = relationship("Track", back_populates="history_items")
    podcast_episode = relationship("PodcastEpisode", back_populates="history_items")
