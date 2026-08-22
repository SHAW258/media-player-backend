from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class PodcastShow(Base):
    __tablename__ = "podcast_shows"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(150), nullable=False)
    host_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    cover_url = Column(String(255), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    total_episodes = Column(Integer, default=0)
    rating = Column(Float, default=5.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    category = relationship("Category", back_populates="podcast_shows")
    episodes = relationship("PodcastEpisode", back_populates="show", cascade="all, delete-orphan")

class PodcastEpisode(Base):
    __tablename__ = "podcast_episodes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    show_id = Column(Integer, ForeignKey("podcast_shows.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    duration_seconds = Column(Integer, nullable=False, default=0)
    audio_url = Column(String(255), nullable=False)
    cover_url = Column(String(255), nullable=True)
    episode_number = Column(Integer, default=1)
    published_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    stream_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    show = relationship("PodcastShow", back_populates="episodes")
    favorites = relationship("Favorite", back_populates="podcast_episode", cascade="all, delete-orphan")
    history_items = relationship("PlaybackHistory", back_populates="podcast_episode")
    queue_items = relationship("UserQueue", back_populates="podcast_episode")
