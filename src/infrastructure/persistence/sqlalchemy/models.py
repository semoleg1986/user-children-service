from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from sqlalchemy import JSON, Date, DateTime, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"

    user_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    children: Mapped[list["ChildModel"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class ChildModel(Base):
    __tablename__ = "children"

    child_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    birthdate: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user: Mapped[UserModel] = relationship(back_populates="children")
    stories: Mapped[list["StoryModel"]] = relationship(
        back_populates="child",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class StoryModel(Base):
    __tablename__ = "stories"

    story_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    child_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("children.child_id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    child: Mapped[ChildModel] = relationship(back_populates="stories")


class AuditEventModel(Base):
    __tablename__ = "audit_events"

    event_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    service: Mapped[str] = mapped_column(String(128), nullable=False)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    actor_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    actor_role: Mapped[str] = mapped_column(String(64), nullable=False)
    target_type: Mapped[str] = mapped_column(String(64), nullable=False)
    target_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    request_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    correlation_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    payload_before: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    payload_after: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    user_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    version_after: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status_after: Mapped[str | None] = mapped_column(String(64), nullable=True)
