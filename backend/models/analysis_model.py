"""
Analysis Result Model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, JSON, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from backend.base import Base


class AnalysisResult(Base):
    """Analysis result model"""
    __tablename__ = "analysis_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True, index=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True, index=True)

    # User insights (JSON fields)
    pain_points = Column(JSON, default=list)
    benefits = Column(JSON, default=list)
    concerns = Column(JSON, default=list)
    use_cases = Column(JSON, default=list)

    # Additional analysis
    sentiment_summary = Column(Text, nullable=True)
    key_themes = Column(JSON, default=list)
    competitor_mentions = Column(JSON, default=list)

    # Raw data reference
    notes_analyzed = Column(Integer, default=0)
    comments_analyzed = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<AnalysisResult(id={self.id}, product_id={self.product_id})>"

    def to_dict(self):
        return {
            "id": str(self.id),
            "product_id": str(self.product_id) if self.product_id else None,
            "task_id": str(self.task_id) if self.task_id else None,
            "pain_points": self.pain_points,
            "benefits": self.benefits,
            "concerns": self.concerns,
            "use_cases": self.use_cases,
            "sentiment_summary": self.sentiment_summary,
            "key_themes": self.key_themes,
            "notes_analyzed": self.notes_analyzed,
            "comments_analyzed": self.comments_analyzed,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
