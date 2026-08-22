from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id", ondelete="CASCADE"), nullable=True)
    podcast_episode_id = Column(Integer, ForeignKey("podcast_episodes.id", ondelete="CASCADE"), nullable=True)
    album_id = Column(Integer, ForeignKey("albums.id", ondelete="CASCADE"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="favorites")
    track = relationship("Track", back_populates="favorites")
    podcast_episode = relationship("PodcastEpisode", back_populates="favorites")
    album = relationship("Album", back_populates="favorites")
