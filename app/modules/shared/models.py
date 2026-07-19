from fastuuid7 import uuid7
from uuid import UUID as UUIDType
from datetime import datetime

from sqlalchemy import MetaData, UUID, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

POSTGRES_NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(constraint_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Base class for all models."""

    metadata = MetaData(naming_convention=POSTGRES_NAMING_CONVENTION)


class UUIDMixin:
    """Mixin class for models with a UUID primary key."""

    id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid7
    )


class CreatedAtMixin:
    """Mixin class for models with a created_at timestamp."""

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )


class TimeStampMixin:
    """Mixin class for models with created_at and updated_at timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
