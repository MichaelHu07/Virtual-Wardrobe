from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declared_attr
from sqlalchemy import MetaData

class Base:
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    metadata = MetaData()

