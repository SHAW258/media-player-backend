from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class Track(Base):
    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(150), nullable=False)
    artist_id = Column(Integer, ForeignKey("artists.id", ondelete="CASCADE"), nullable=False)
    album_id = Column(Integer, ForeignKey("albums.id", ondelete="SET NULL"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    duration_seconds = Column(Integer, nullable=False, default=0)
    audio_url = Column(String(255), nullable=False)
    cover_url = Column(String(255), nullable=True)
    lyrics = Column(Text, nullable=True)
    stream_count = Column(Integer, default=0, index=True)
    is_trending = Column(Boolean, default=False, index=True)
    is_new_release = Column(Boolean, default=False)
    media_type = Column(String(20), default="music", index=True)  # 'music', 'podcast'
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    artist = relationship("Artist", back_populates="tracks")
    album = relationship("Album", back_populates="tracks")
    category = relationship("Category", back_populates="tracks")
    playlist_items = relationship("PlaylistTrack", back_populates="track", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="track", cascade="all, delete-orphan")
    history_items = relationship("PlaybackHistory", back_populates="track")
    queue_items = relationship("UserQueue", back_populates="track")
