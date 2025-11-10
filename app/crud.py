"""CRUD operations for Python MCP Chat."""
from datetime import datetime
from typing import Optional
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import Session
from app.models import Message, Reaction


def send_message(db: Session, name: str, content: str, channel: str = "general") -> int:
    """Send a new message."""
    message = Message(name=name, content=content, channel=channel)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message.id


def get_messages(db: Session, limit: int = 50) -> list[dict]:
    """Get recent messages with reply and reaction counts."""
    # Subquery for reply count
    reply_count_subq = (
        select(func.count(Message.id))
        .where(Message.parent_id == Message.id)
        .correlate(Message)
        .scalar_subquery()
    )
    
    # Subquery for reaction count
    reaction_count_subq = (
        select(func.count(Reaction.id))
        .where(Reaction.message_id == Message.id)
        .correlate(Message)
        .scalar_subquery()
    )
    
    stmt = (
        select(
            Message,
            reply_count_subq.label('reply_count'),
            reaction_count_subq.label('reaction_count')
        )
        .where(Message.parent_id.is_(None))
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    
    results = db.execute(stmt).all()
    
    messages = []
    for row in results:
        msg = row[0]
        messages.append({
            'id': msg.id,
            'name': msg.name,
            'content': msg.content,
            'channel': msg.channel,
            'parent_id': msg.parent_id,
            'created_at': msg.created_at.isoformat(),
            'updated_at': msg.updated_at.isoformat(),
            'reply_count': row[1] or 0,
            'reaction_count': row[2] or 0
        })
    
    return messages


def reply_to_message(db: Session, parent_id: int, name: str, content: str) -> int:
    """Reply to a message (inherits channel from parent)."""
    # Get parent message
    parent = db.execute(
        select(Message).where(Message.id == parent_id)
    ).scalar_one_or_none()
    
    if not parent:
        raise ValueError(f"Parent message {parent_id} not found")
    
    # Create reply with inherited channel
    reply = Message(
        parent_id=parent_id,
        name=name,
        content=content,
        channel=parent.channel
    )
    db.add(reply)
    db.commit()
    db.refresh(reply)
    return reply.id


def get_message_by_id(db: Session, message_id: int) -> Optional[dict]:
    """Get a message by ID."""
    msg = db.execute(
        select(Message).where(Message.id == message_id)
    ).scalar_one_or_none()
    
    if not msg:
        return None
    
    return {
        'id': msg.id,
        'name': msg.name,
        'content': msg.content,
        'channel': msg.channel,
        'parent_id': msg.parent_id,
        'created_at': msg.created_at.isoformat(),
        'updated_at': msg.updated_at.isoformat()
    }


def get_message_thread(db: Session, message_id: int) -> Optional[dict]:
    """Get a message thread with parent and replies."""
    msg = db.execute(
        select(Message).where(Message.id == message_id)
    ).scalar_one_or_none()
    
    if not msg:
        return None
    
    # Get replies
    replies_stmt = (
        select(Message)
        .where(Message.parent_id == message_id)
        .order_by(Message.created_at.asc())
    )
    replies = db.execute(replies_stmt).scalars().all()
    
    result = {
        'id': msg.id,
        'name': msg.name,
        'content': msg.content,
        'channel': msg.channel,
        'parent_id': msg.parent_id,
        'created_at': msg.created_at.isoformat(),
        'updated_at': msg.updated_at.isoformat(),
        'reply_count': len(replies),
        'replies': [
            {
                'id': r.id,
                'name': r.name,
                'content': r.content,
                'created_at': r.created_at.isoformat()
            }
            for r in replies
        ]
    }
    
    # Add parent if exists
    if msg.parent_id:
        parent = db.execute(
            select(Message).where(Message.id == msg.parent_id)
        ).scalar_one_or_none()
        if parent:
            result['parent'] = {
                'id': parent.id,
                'name': parent.name,
                'content': parent.content,
                'created_at': parent.created_at.isoformat()
            }
    
    return result


def get_channels(db: Session) -> list[dict]:
    """Get all channels with message count and last activity."""
    stmt = (
        select(
            Message.channel,
            func.count(Message.id).label('message_count'),
            func.max(Message.created_at).label('last_activity')
        )
        .group_by(Message.channel)
        .order_by(Message.channel)
    )
    
    results = db.execute(stmt).all()
    
    return [
        {
            'channel': row[0],
            'message_count': row[1],
            'last_activity': row[2].isoformat() if row[2] else None
        }
        for row in results
    ]


def get_channel_messages(db: Session, channel: str, limit: int = 50) -> list[dict]:
    """Get messages from a specific channel."""
    # Subquery for reply count
    reply_count_subq = (
        select(func.count(Message.id))
        .where(Message.parent_id == Message.id)
        .correlate(Message)
        .scalar_subquery()
    )
    
    # Subquery for reaction count
    reaction_count_subq = (
        select(func.count(Reaction.id))
        .where(Reaction.message_id == Message.id)
        .correlate(Message)
        .scalar_subquery()
    )
    
    stmt = (
        select(
            Message,
            reply_count_subq.label('reply_count'),
            reaction_count_subq.label('reaction_count')
        )
        .where(Message.channel == channel)
        .where(Message.parent_id.is_(None))
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    
    results = db.execute(stmt).all()
    
    messages = []
    for row in results:
        msg = row[0]
        messages.append({
            'id': msg.id,
            'name': msg.name,
            'content': msg.content,
            'channel': msg.channel,
            'parent_id': msg.parent_id,
            'created_at': msg.created_at.isoformat(),
            'updated_at': msg.updated_at.isoformat(),
            'reply_count': row[1] or 0,
            'reaction_count': row[2] or 0
        })
    
    return messages


def add_reaction(db: Session, message_id: int, user_name: str, emoji: str) -> None:
    """Add a reaction to a message."""
    # Check if message exists
    msg = db.execute(
        select(Message).where(Message.id == message_id)
    ).scalar_one_or_none()
    
    if not msg:
        raise ValueError(f"Message {message_id} not found")
    
    # Check if reaction already exists
    existing = db.execute(
        select(Reaction).where(
            and_(
                Reaction.message_id == message_id,
                Reaction.user_name == user_name,
                Reaction.emoji == emoji
            )
        )
    ).scalar_one_or_none()
    
    if existing:
        raise ValueError(f"Reaction already exists")
    
    reaction = Reaction(message_id=message_id, user_name=user_name, emoji=emoji)
    db.add(reaction)
    db.commit()


def remove_reaction(db: Session, message_id: int, user_name: str, emoji: str) -> None:
    """Remove a reaction from a message."""
    reaction = db.execute(
        select(Reaction).where(
            and_(
                Reaction.message_id == message_id,
                Reaction.user_name == user_name,
                Reaction.emoji == emoji
            )
        )
    ).scalar_one_or_none()
    
    if not reaction:
        raise ValueError(f"Reaction not found")
    
    db.delete(reaction)
    db.commit()


def get_message_reactions(db: Session, message_id: int) -> dict:
    """Get reactions for a message, grouped by emoji."""
    stmt = (
        select(Reaction)
        .where(Reaction.message_id == message_id)
        .order_by(Reaction.created_at.asc())
    )
    
    reactions = db.execute(stmt).scalars().all()
    
    # Group by emoji
    grouped = {}
    for reaction in reactions:
        if reaction.emoji not in grouped:
            grouped[reaction.emoji] = []
        grouped[reaction.emoji].append({
            'user_name': reaction.user_name,
            'created_at': reaction.created_at.isoformat()
        })
    
    return {
        'message_id': message_id,
        'reactions': grouped,
        'total_count': len(reactions)
    }


def get_users_list(db: Session, limit: int = 50, sort_by: str = "name") -> list[dict]:
    """Get list of users with message count and last activity."""
    stmt = (
        select(
            Message.name,
            func.count(Message.id).label('message_count'),
            func.max(Message.created_at).label('last_activity')
        )
        .group_by(Message.name)
    )
    
    if sort_by == "name":
        stmt = stmt.order_by(Message.name)
    elif sort_by == "messages":
        stmt = stmt.order_by(func.count(Message.id).desc())
    elif sort_by == "last_activity":
        stmt = stmt.order_by(func.max(Message.created_at).desc())
    
    stmt = stmt.limit(limit)
    
    results = db.execute(stmt).all()
    
    return [
        {
            'name': row[0],
            'message_count': row[1],
            'last_activity': row[2].isoformat() if row[2] else None
        }
        for row in results
    ]


def search_messages(db: Session, query: str, limit: int = 50) -> list[dict]:
    """Search messages by content or name (case-insensitive)."""
    search_pattern = f"%{query}%"
    
    # Subquery for reply count
    reply_count_subq = (
        select(func.count(Message.id))
        .where(Message.parent_id == Message.id)
        .correlate(Message)
        .scalar_subquery()
    )
    
    # Subquery for reaction count
    reaction_count_subq = (
        select(func.count(Reaction.id))
        .where(Reaction.message_id == Message.id)
        .correlate(Message)
        .scalar_subquery()
    )
    
    stmt = (
        select(
            Message,
            reply_count_subq.label('reply_count'),
            reaction_count_subq.label('reaction_count')
        )
        .where(
            or_(
                Message.content.ilike(search_pattern),
                Message.name.ilike(search_pattern)
            )
        )
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    
    results = db.execute(stmt).all()
    
    messages = []
    for row in results:
        msg = row[0]
        messages.append({
            'id': msg.id,
            'name': msg.name,
            'content': msg.content,
            'channel': msg.channel,
            'parent_id': msg.parent_id,
            'created_at': msg.created_at.isoformat(),
            'updated_at': msg.updated_at.isoformat(),
            'reply_count': row[1] or 0,
            'reaction_count': row[2] or 0
        })
    
    return messages


def get_messages_by_user(db: Session, name: str, limit: int = 50) -> list[dict]:
    """Get messages by user (partial match on name)."""
    search_pattern = f"%{name}%"
    
    # Subquery for reply count
    reply_count_subq = (
        select(func.count(Message.id))
        .where(Message.parent_id == Message.id)
        .correlate(Message)
        .scalar_subquery()
    )
    
    # Subquery for reaction count
    reaction_count_subq = (
        select(func.count(Reaction.id))
        .where(Reaction.message_id == Message.id)
        .correlate(Message)
        .scalar_subquery()
    )
    
    stmt = (
        select(
            Message,
            reply_count_subq.label('reply_count'),
            reaction_count_subq.label('reaction_count')
        )
        .where(Message.name.ilike(search_pattern))
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    
    results = db.execute(stmt).all()
    
    messages = []
    for row in results:
        msg = row[0]
        messages.append({
            'id': msg.id,
            'name': msg.name,
            'content': msg.content,
            'channel': msg.channel,
            'parent_id': msg.parent_id,
            'created_at': msg.created_at.isoformat(),
            'updated_at': msg.updated_at.isoformat(),
            'reply_count': row[1] or 0,
            'reaction_count': row[2] or 0
        })
    
    return messages


def get_messages_by_date_range(
    db: Session, 
    start_date: datetime, 
    end_date: datetime, 
    limit: int = 50
) -> list[dict]:
    """Get messages within a date range."""
    # Subquery for reply count
    reply_count_subq = (
        select(func.count(Message.id))
        .where(Message.parent_id == Message.id)
        .correlate(Message)
        .scalar_subquery()
    )
    
    # Subquery for reaction count
    reaction_count_subq = (
        select(func.count(Reaction.id))
        .where(Reaction.message_id == Message.id)
        .correlate(Message)
        .scalar_subquery()
    )
    
    stmt = (
        select(
            Message,
            reply_count_subq.label('reply_count'),
            reaction_count_subq.label('reaction_count')
        )
        .where(
            and_(
                Message.created_at >= start_date,
                Message.created_at <= end_date
            )
        )
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    
    results = db.execute(stmt).all()
    
    messages = []
    for row in results:
        msg = row[0]
        messages.append({
            'id': msg.id,
            'name': msg.name,
            'content': msg.content,
            'channel': msg.channel,
            'parent_id': msg.parent_id,
            'created_at': msg.created_at.isoformat(),
            'updated_at': msg.updated_at.isoformat(),
            'reply_count': row[1] or 0,
            'reaction_count': row[2] or 0
        })
    
    return messages
