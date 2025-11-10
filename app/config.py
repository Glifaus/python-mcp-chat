"""Configuration for Python MCP Chat."""
import os
from pathlib import Path

# Database configuration
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/chat.db")

# Allowed emojis for reactions
ALLOWED_EMOJIS = [
    "👍", "❤️", "😂", "🎉", "🚀", "👏", 
    "🔥", "💯", "👎", "😮", "😢", "😡", 
    "🤔", "💡", "✅", "❌"
]
