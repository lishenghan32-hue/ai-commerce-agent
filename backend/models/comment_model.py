"""
Comment Model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from backend.base import Base


class Comment(Base):
    """Comment model"""
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id"), nullable=True, index=True)
    platform = Column(String(50), default="xiaohongshu", nullable=False)
    comment_id = Column(String(255), nullable=True, index=True)  # Platform's comment ID
    parent_comment_id = Column(String(255), nullable=True)  # For reply comments
    user_id = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)
    text = Column(Text, nullable=False)
    like_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Comment(id={self.id}, text={self.text[:50]}...)>"

    def to_dict(self):
        return {
            "id": str(self.id),
            "note_id": str(self.note_id) if self.note_id else None,
            "platform": self.platform,
            "comment_id": self.comment_id,
            "parent_comment_id": self.parent_comment_id,
            "username": self.username,
            "text": self.text,
            "like_count": self.like_count,
            "reply_count": self.reply_count,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
