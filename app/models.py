"""SQLAlchemy models for Python MCP Chat."""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Message(Base):
    """Message model representing chat messages."""
    __tablename__ = "messages"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE"), 
        nullable=True
    )
    name: Mapped[str] = mapped_column(String(50))
    content: Mapped[str] = mapped_column(String(500))
    channel: Mapped[str] = mapped_column(String(50), default="general", index=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    
    # Relationships with cascade
    parent: Mapped[Optional["Message"]] = relationship(
        "Message",
        back_populates="replies", 
        remote_side=[id],
        foreign_keys=[parent_id]
    )
    replies: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="parent", 
        cascade="all, delete-orphan",
        foreign_keys=[parent_id]
    )
    reactions: Mapped[list["Reaction"]] = relationship(
        "Reaction",
        back_populates="message", 
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index('ix_messages_parent_id', 'parent_id'),
        Index('ix_messages_created_at', 'created_at'),
    )


class Reaction(Base):
    """Reaction model representing emoji reactions to messages."""
    __tablename__ = "reactions"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    message_id: Mapped[int] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE")
    )
    user_name: Mapped[str] = mapped_column(String(50))
    emoji: Mapped[str] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    
    message: Mapped["Message"] = relationship("Message", back_populates="reactions")
    
    __table_args__ = (
        UniqueConstraint('message_id', 'user_name', 'emoji', name='uix_message_user_emoji'),
        Index('ix_reactions_message_id', 'message_id'),
    )
