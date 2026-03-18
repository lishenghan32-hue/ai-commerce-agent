"""
Note Model (Xiaohongshu)
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from backend.base import Base


class Note(Base):
    """Note model for Xiaohongshu posts"""
    __tablename__ = "notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True, index=True)
    platform = Column(String(50), default="xiaohongshu", nullable=False)
    note_id = Column(String(255), nullable=True, index=True)  # Platform's note ID
    title = Column(String(500), nullable=True)
    author = Column(String(255), nullable=True)
    author_id = Column(String(255), nullable=True)
    like_count = Column(Integer, default=0)
    collect_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    url = Column(String(1000), nullable=True)
    cover_image = Column(String(1000), nullable=True)
    content = Column(Text, nullable=True)
    tags = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Note(id={self.id}, title={self.title})>"

    def to_dict(self):
        return {
            "id": str(self.id),
            "product_id": str(self.product_id) if self.product_id else None,
            "platform": self.platform,
            "note_id": self.note_id,
            "title": self.title,
            "author": self.author,
            "like_count": self.like_count,
            "collect_count": self.collect_count,
            "comment_count": self.comment_count,
            "url": self.url,
            "content": self.content,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
