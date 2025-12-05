from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.session import Base

class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class UserAvatar(Base, TimestampMixin):
    __tablename__ = "user_avatars"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(String, index=True, nullable=False) # External User ID (e.g. Auth0)
    image_url = Column(String, nullable=False)
    pose_data = Column(JSONB, nullable=True) # Keypoints
    is_processed = Column(Boolean, default=False)
    meta_data = Column(JSONB, default={})

class GarmentItem(Base, TimestampMixin):
    __tablename__ = "garment_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    category = Column(String, index=True, nullable=False) # e.g., 'upper_body', 'lower_body'
    image_url = Column(String, nullable=False)
    mask_url = Column(String, nullable=True)
    texture_data = Column(JSONB, nullable=True)
    is_active = Column(Boolean, default=True)

class TryOnResult2D(Base, TimestampMixin):
    __tablename__ = "tryon_results_2d"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_avatar_id = Column(UUID(as_uuid=True), ForeignKey("user_avatars.id"), nullable=False, index=True)
    garment_item_id = Column(UUID(as_uuid=True), ForeignKey("garment_items.id"), nullable=False, index=True)
    result_image_url = Column(String, nullable=False)
    processing_time_ms = Column(String, nullable=True)
    
    avatar = relationship("UserAvatar")
    garment = relationship("GarmentItem")

class TryOnResult3D(Base, TimestampMixin):
    __tablename__ = "tryon_results_3d"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_avatar_id = Column(UUID(as_uuid=True), ForeignKey("user_avatars.id"), nullable=False, index=True)
    garment_item_ids = Column(JSONB, nullable=False) # List of garment IDs
    model_glb_url = Column(String, nullable=False)
    preview_image_url = Column(String, nullable=True)
    status = Column(String, default="pending") # pending, processing, completed, failed
    
    avatar = relationship("UserAvatar")

