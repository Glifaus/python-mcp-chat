"""MCP Server for Python MCP Chat."""
import asyncio
import json
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from app.database import SessionLocal, init_db
from app import crud, schemas
from app.config import ALLOWED_EMOJIS


app = Server("python-mcp-chat")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools."""
    return [
        Tool(
            name="send-message",
            description="Send a message to a channel",
            inputSchema=schemas.SendMessageInput.model_json_schema()
        ),
        Tool(
            name="get-messages",
            description="Get recent messages with reply and reaction counts",
            inputSchema=schemas.GetMessagesInput.model_json_schema()
        ),
        Tool(
            name="reply-to-message",
            description="Reply to a message (creates a thread)",
            inputSchema=schemas.ReplyToMessageInput.model_json_schema()
        ),
        Tool(
            name="get-message-thread",
            description="Get a message thread with parent and all replies",
            inputSchema=schemas.GetMessageThreadInput.model_json_schema()
        ),
        Tool(
            name="get-channels",
            description="Get all channels with message count and last activity",
            inputSchema={}
        ),
        Tool(
            name="get-channel-messages",
            description="Get messages from a specific channel",
            inputSchema=schemas.GetChannelMessagesInput.model_json_schema()
        ),
        Tool(
            name="add-reaction",
            description=f"Add an emoji reaction to a message. Allowed emojis: {', '.join(ALLOWED_EMOJIS)}",
            inputSchema=schemas.AddReactionInput.model_json_schema()
        ),
        Tool(
            name="remove-reaction",
            description="Remove an emoji reaction from a message",
            inputSchema=schemas.RemoveReactionInput.model_json_schema()
        ),
        Tool(
            name="get-message-reactions",
            description="Get all reactions for a message, grouped by emoji",
            inputSchema=schemas.GetMessageReactionsInput.model_json_schema()
        ),
        Tool(
            name="get-users-list",
            description="Get list of users with message count and last activity",
            inputSchema=schemas.GetUsersListInput.model_json_schema()
        ),
        Tool(
            name="search-messages",
            description="Search messages by content or name (case-insensitive)",
            inputSchema=schemas.SearchMessagesInput.model_json_schema()
        ),
        Tool(
            name="get-messages-by-user",
            description="Get messages by a specific user (partial match)",
            inputSchema=schemas.GetMessagesByUserInput.model_json_schema()
        ),
        Tool(
            name="get-messages-by-date-range",
            description="Get messages within a date range",
            inputSchema=schemas.GetMessagesByDateRangeInput.model_json_schema()
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    db = SessionLocal()
    try:
        if name == "send-message":
            data = schemas.SendMessageInput(**arguments)
            msg_id = crud.send_message(db, data.name, data.content, data.channel)
            return [TextContent(
                type="text", 
                text=f"✅ Message {msg_id} sent to #{data.channel} by {data.name}"
            )]
        
        elif name == "get-messages":
            data = schemas.GetMessagesInput(**arguments)
            messages = crud.get_messages(db, data.limit)
            return [TextContent(
                type="text",
                text=f"📨 Found {len(messages)} messages:\n\n{json.dumps(messages, indent=2)}"
            )]
        
        elif name == "reply-to-message":
            data = schemas.ReplyToMessageInput(**arguments)
            reply_id = crud.reply_to_message(
                db, 
                data.parent_message_id, 
                data.name, 
                data.content
            )
            return [TextContent(
                type="text",
                text=f"✅ Reply {reply_id} added to message {data.parent_message_id} by {data.name}"
            )]
        
        elif name == "get-message-thread":
            data = schemas.GetMessageThreadInput(**arguments)
            thread = crud.get_message_thread(db, data.message_id)
            if not thread:
                return [TextContent(
                    type="text",
                    text=f"❌ Message {data.message_id} not found"
                )]
            return [TextContent(
                type="text",
                text=f"🧵 Thread for message {data.message_id}:\n\n{json.dumps(thread, indent=2)}"
            )]
        
        elif name == "get-channels":
            channels = crud.get_channels(db)
            return [TextContent(
                type="text",
                text=f"📂 Found {len(channels)} channels:\n\n{json.dumps(channels, indent=2)}"
            )]
        
        elif name == "get-channel-messages":
            data = schemas.GetChannelMessagesInput(**arguments)
            messages = crud.get_channel_messages(db, data.channel, data.limit)
            return [TextContent(
                type="text",
                text=f"📨 Found {len(messages)} messages in #{data.channel}:\n\n{json.dumps(messages, indent=2)}"
            )]
        
        elif name == "add-reaction":
            data = schemas.AddReactionInput(**arguments)
            crud.add_reaction(db, data.message_id, data.user_name, data.emoji)
            return [TextContent(
                type="text",
                text=f"✅ Reaction {data.emoji} added to message {data.message_id} by {data.user_name}"
            )]
        
        elif name == "remove-reaction":
            data = schemas.RemoveReactionInput(**arguments)
            crud.remove_reaction(db, data.message_id, data.user_name, data.emoji)
            return [TextContent(
                type="text",
                text=f"✅ Reaction {data.emoji} removed from message {data.message_id} by {data.user_name}"
            )]
        
        elif name == "get-message-reactions":
            data = schemas.GetMessageReactionsInput(**arguments)
            reactions = crud.get_message_reactions(db, data.message_id)
            return [TextContent(
                type="text",
                text=f"😊 Reactions for message {data.message_id}:\n\n{json.dumps(reactions, indent=2)}"
            )]
        
        elif name == "get-users-list":
            data = schemas.GetUsersListInput(**arguments)
            users = crud.get_users_list(db, data.limit, data.sort_by)
            return [TextContent(
                type="text",
                text=f"👥 Found {len(users)} users (sorted by {data.sort_by}):\n\n{json.dumps(users, indent=2)}"
            )]
        
        elif name == "search-messages":
            data = schemas.SearchMessagesInput(**arguments)
            messages = crud.search_messages(db, data.query, data.limit)
            return [TextContent(
                type="text",
                text=f"🔍 Found {len(messages)} messages matching '{data.query}':\n\n{json.dumps(messages, indent=2)}"
            )]
        
        elif name == "get-messages-by-user":
            data = schemas.GetMessagesByUserInput(**arguments)
            messages = crud.get_messages_by_user(db, data.name, data.limit)
            return [TextContent(
                type="text",
                text=f"👤 Found {len(messages)} messages by '{data.name}':\n\n{json.dumps(messages, indent=2)}"
            )]
        
        elif name == "get-messages-by-date-range":
            data = schemas.GetMessagesByDateRangeInput(**arguments)
            messages = crud.get_messages_by_date_range(
                db, 
                data.start_date, 
                data.end_date, 
                data.limit
            )
            return [TextContent(
                type="text",
                text=f"📅 Found {len(messages)} messages between {data.start_date} and {data.end_date}:\n\n{json.dumps(messages, indent=2)}"
            )]
        
        else:
            return [TextContent(
                type="text",
                text=f"❌ Unknown tool: {name}"
            )]
    
    except ValueError as e:
        return [TextContent(type="text", text=f"❌ Validation error: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Error: {str(e)}")]
    finally:
        db.close()


async def main():
    """Main entry point for the MCP server."""
    init_db()
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream, 
            write_stream, 
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
