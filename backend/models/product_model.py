"""
Product Model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from backend.base import Base


class Product(Base):
    """Product model"""
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(500), nullable=False, index=True)
    brand = Column(String(255), nullable=True)
    category = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    product_url = Column(String(1000), nullable=True)
    image_url = Column(String(1000), nullable=True)
    price = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name})>"

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "brand": self.brand,
            "category": self.category,
            "description": self.description,
            "product_url": self.product_url,
            "image_url": self.image_url,
            "price": self.price,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
