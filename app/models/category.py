from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    category_type = Column(String(20), default="both")  # 'music', 'podcast', 'both'
    icon = Column(String(100), nullable=True)
    cover_image = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    artists = relationship("Artist", back_populates="category")
    tracks = relationship("Track", back_populates="category")
    podcast_shows = relationship("PodcastShow", back_populates="category")
