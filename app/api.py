"""Optional FastAPI REST API for Python MCP Chat."""
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas


api = FastAPI(
    title="Python MCP Chat API",
    description="REST API for Python MCP Chat",
    version="1.0.0"
)


@api.get("/")
def root():
    """Root endpoint."""
    return {
        "name": "Python MCP Chat API",
        "version": "1.0.0",
        "status": "running"
    }


@api.get("/messages", response_model=list[dict])
def list_messages(limit: int = 50, db: Session = Depends(get_db)):
    """Get recent messages."""
    return crud.get_messages(db, limit)


@api.post("/messages", response_model=dict)
def create_message(msg: schemas.SendMessageInput, db: Session = Depends(get_db)):
    """Send a new message."""
    msg_id = crud.send_message(db, msg.name, msg.content, msg.channel)
    return {"id": msg_id, "message": "Message created successfully"}


@api.get("/messages/{message_id}", response_model=dict)
def get_message(message_id: int, db: Session = Depends(get_db)):
    """Get a specific message."""
    message = crud.get_message_by_id(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message


@api.get("/messages/{message_id}/thread", response_model=dict)
def get_thread(message_id: int, db: Session = Depends(get_db)):
    """Get a message thread."""
    thread = crud.get_message_thread(db, message_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Message not found")
    return thread


@api.post("/messages/{message_id}/replies", response_model=dict)
def create_reply(
    message_id: int, 
    reply: schemas.ReplyToMessageInput,
    db: Session = Depends(get_db)
):
    """Reply to a message."""
    try:
        reply_id = crud.reply_to_message(
            db, 
            reply.parent_message_id, 
            reply.name, 
            reply.content
        )
        return {"id": reply_id, "message": "Reply created successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@api.get("/channels", response_model=list[dict])
def list_channels(db: Session = Depends(get_db)):
    """Get all channels."""
    return crud.get_channels(db)


@api.get("/channels/{channel}/messages", response_model=list[dict])
def get_channel_messages(
    channel: str, 
    limit: int = 50, 
    db: Session = Depends(get_db)
):
    """Get messages from a specific channel."""
    return crud.get_channel_messages(db, channel, limit)


@api.post("/messages/{message_id}/reactions", response_model=dict)
def add_reaction(
    message_id: int,
    reaction: schemas.AddReactionInput,
    db: Session = Depends(get_db)
):
    """Add a reaction to a message."""
    try:
        crud.add_reaction(db, reaction.message_id, reaction.user_name, reaction.emoji)
        return {"message": "Reaction added successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@api.delete("/messages/{message_id}/reactions", response_model=dict)
def remove_reaction(
    message_id: int,
    reaction: schemas.RemoveReactionInput,
    db: Session = Depends(get_db)
):
    """Remove a reaction from a message."""
    try:
        crud.remove_reaction(db, reaction.message_id, reaction.user_name, reaction.emoji)
        return {"message": "Reaction removed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@api.get("/messages/{message_id}/reactions", response_model=dict)
def get_reactions(message_id: int, db: Session = Depends(get_db)):
    """Get reactions for a message."""
    return crud.get_message_reactions(db, message_id)


@api.get("/users", response_model=list[dict])
def list_users(
    limit: int = 50, 
    sort_by: str = "name",
    db: Session = Depends(get_db)
):
    """Get list of users."""
    return crud.get_users_list(db, limit, sort_by)


@api.get("/search", response_model=list[dict])
def search_messages(query: str, limit: int = 50, db: Session = Depends(get_db)):
    """Search messages."""
    return crud.search_messages(db, query, limit)


@api.get("/users/{name}/messages", response_model=list[dict])
def get_user_messages(name: str, limit: int = 50, db: Session = Depends(get_db)):
    """Get messages by user."""
    return crud.get_messages_by_user(db, name, limit)


@api.get("/messages/date-range", response_model=list[dict])
def get_messages_by_date(
    start_date: datetime,
    end_date: datetime,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get messages by date range."""
    return crud.get_messages_by_date_range(db, start_date, end_date, limit)
