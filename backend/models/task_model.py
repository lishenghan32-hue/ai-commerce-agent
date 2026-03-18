"""
Task Model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from backend.base import Base


class Task(Base):
    """Task model for tracking analysis pipeline"""
    __tablename__ = "tasks"

    # Task status constants
    STATUS_PENDING = "pending"
    STATUS_RUNNING = "running"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"
    STATUS_CANCELLED = "cancelled"

    # Task types
    TYPE_ANALYSIS = "analysis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_type = Column(String(50), default=TYPE_ANALYSIS, nullable=False)
    status = Column(String(50), default=STATUS_PENDING, nullable=False, index=True)

    # Progress tracking
    progress = Column(Integer, default=0)
    current_step = Column(String(100), nullable=True)

    # Input
    product_url = Column(String(1000), nullable=True)

    # Related entities
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True)
    analysis_result_id = Column(UUID(as_uuid=True), ForeignKey("analysis_results.id"), nullable=True)

    # Results
    live_script = Column(JSON, default=dict)
    ppt_url = Column(Text, nullable=True)

    # Error handling
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, default=dict)

    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Task(id={self.id}, status={self.status}, progress={self.progress})>"

    def to_dict(self):
        return {
            "id": str(self.id),
            "task_type": self.task_type,
            "status": self.status,
            "progress": self.progress,
            "current_step": self.current_step,
            "product_url": self.product_url,
            "product_id": str(self.product_id) if self.product_id else None,
            "error_message": self.error_message,
            "live_script": self.live_script,
            "ppt_url": self.ppt_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }
