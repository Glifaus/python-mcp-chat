"""Pydantic schemas for validation."""
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator
from app.config import ALLOWED_EMOJIS


class SendMessageInput(BaseModel):
    """Schema for sending a message."""
    name: str = Field(..., min_length=1, max_length=50)
    content: str = Field(..., min_length=1, max_length=500)
    channel: str = Field(default="general", max_length=50)


class GetMessagesInput(BaseModel):
    """Schema for getting recent messages."""
    limit: int = Field(default=50, ge=1, le=100)


class ReplyToMessageInput(BaseModel):
    """Schema for replying to a message."""
    parent_message_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=50)
    content: str = Field(..., min_length=1, max_length=500)


class GetMessageThreadInput(BaseModel):
    """Schema for getting a message thread."""
    message_id: int = Field(..., gt=0)


class GetChannelMessagesInput(BaseModel):
    """Schema for getting messages from a channel."""
    channel: str = Field(..., max_length=50)
    limit: int = Field(default=50, ge=1, le=100)


class AddReactionInput(BaseModel):
    """Schema for adding a reaction."""
    message_id: int = Field(..., gt=0)
    user_name: str = Field(..., min_length=1, max_length=50)
    emoji: str = Field(..., max_length=10)
    
    @field_validator('emoji')
    @classmethod
    def validate_emoji(cls, v: str) -> str:
        if v not in ALLOWED_EMOJIS:
            raise ValueError(f'Emoji must be one of: {", ".join(ALLOWED_EMOJIS)}')
        return v


class RemoveReactionInput(BaseModel):
    """Schema for removing a reaction."""
    message_id: int = Field(..., gt=0)
    user_name: str = Field(..., min_length=1, max_length=50)
    emoji: str = Field(..., max_length=10)


class GetMessageReactionsInput(BaseModel):
    """Schema for getting message reactions."""
    message_id: int = Field(..., gt=0)


class GetUsersListInput(BaseModel):
    """Schema for getting users list."""
    limit: int = Field(default=50, ge=1, le=100)
    sort_by: Literal["name", "messages", "last_activity"] = Field(default="name")


class SearchMessagesInput(BaseModel):
    """Schema for searching messages."""
    query: str = Field(..., min_length=1, max_length=200)
    limit: int = Field(default=50, ge=1, le=100)


class GetMessagesByUserInput(BaseModel):
    """Schema for getting messages by user."""
    name: str = Field(..., min_length=1, max_length=50)
    limit: int = Field(default=50, ge=1, le=100)


class GetMessagesByDateRangeInput(BaseModel):
    """Schema for getting messages by date range."""
    start_date: datetime
    end_date: datetime
    limit: int = Field(default=50, ge=1, le=100)
