import json
from uuid import UUID
from typing import Optional, List, Type, TypeVar, Generic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.dialects.postgresql import insert as pg_insert
from redis.asyncio import Redis

from app.models.wardrobe import UserAvatar, GarmentItem, TryOnResult2D, TryOnResult3D
from app.schemas.wardrobe import UserAvatarCreate, GarmentItemCreate, TryOnResult2DCreate, TryOnResult3DCreate
from app.core.config import settings

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")

class BaseService(Generic[ModelType, CreateSchemaType]):
    def __init__(self, model: Type[ModelType], redis: Redis):
        self.model = model
        self.redis = redis
        self.cache_ttl = 3600  # 1 hour

    async def get(self, db: AsyncSession, id: UUID) -> Optional[ModelType]:
        # Try Cache
        cache_key = f"{self.model.__tablename__}:{id}"
        cached = await self.redis.get(cache_key)
        if cached:
            # Assuming simple JSON serialization for demo; real world needs proper decoder
            # This part is simplified. For Pydantic models, .model_validate_json is good.
            # But we are returning SQLAlchemy models here.
            # Skipping complex deserialization for this scaffold.
            pass

        query = select(self.model).where(self.model.id == id)
        result = await db.execute(query)
        obj = result.scalar_one_or_none()
        
        # Set Cache (Not implemented fully for SQLA objects serialization)
        return obj

    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

class WardrobeService:
    def __init__(self):
        self.redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.avatars = BaseService[UserAvatar, UserAvatarCreate](UserAvatar, self.redis)
        self.garments = BaseService[GarmentItem, GarmentItemCreate](GarmentItem, self.redis)
        self.results_2d = BaseService[TryOnResult2D, TryOnResult2DCreate](TryOnResult2D, self.redis)
        self.results_3d = BaseService[TryOnResult3D, TryOnResult3DCreate](TryOnResult3D, self.redis)

    async def upsert_avatar(self, db: AsyncSession, obj_in: UserAvatarCreate) -> UserAvatar:
        """
        Efficient Upsert for User Avatar based on user_id.
        """
        stmt = pg_insert(UserAvatar).values(**obj_in.model_dump())
        stmt = stmt.on_conflict_do_update(
            index_elements=[UserAvatar.user_id], # Requires Unique Index on user_id in DB
            set_=obj_in.model_dump(exclude={'user_id'}) # Update everything else
        )
        # Note: on_conflict_do_update requires a unique constraint/index on user_id.
        # Ensure alembic migration creates this unique constraint.
        
        # SQLAlchemy 2.0 returns result for insert...returning
        stmt = stmt.returning(UserAvatar)
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one()

    async def get_user_garments(self, db: AsyncSession, category: Optional[str] = None) -> List[GarmentItem]:
        query = select(GarmentItem).where(GarmentItem.is_active == True)
        if category:
            query = query.where(GarmentItem.category == category)
        result = await db.execute(query)
        return result.scalars().all()

wardrobe_service = WardrobeService()

