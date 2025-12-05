from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, ConfigDict

# Base Models
class UserAvatarBase(BaseModel):
    user_id: str
    image_url: str
    pose_data: Optional[Dict[str, Any]] = None
    meta_data: Optional[Dict[str, Any]] = {}

class GarmentItemBase(BaseModel):
    category: str
    image_url: str
    mask_url: Optional[str] = None
    texture_data: Optional[Dict[str, Any]] = None
    is_active: bool = True

class TryOnResult2DBase(BaseModel):
    user_avatar_id: UUID
    garment_item_id: UUID
    result_image_url: str
    processing_time_ms: Optional[str] = None

class TryOnResult3DBase(BaseModel):
    user_avatar_id: UUID
    garment_item_ids: List[UUID]
    status: str = "pending"

# Create Models
class UserAvatarCreate(UserAvatarBase):
    pass

class GarmentItemCreate(GarmentItemBase):
    pass

class TryOnResult2DCreate(TryOnResult2DBase):
    pass

class TryOnResult3DCreate(TryOnResult3DBase):
    pass

# Response Models
class UserAvatarResponse(UserAvatarBase):
    id: UUID
    is_processed: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class GarmentItemResponse(GarmentItemBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TryOnResult2DResponse(TryOnResult2DBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TryOnResult3DResponse(TryOnResult3DBase):
    id: UUID
    model_glb_url: Optional[str] = None
    preview_image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

