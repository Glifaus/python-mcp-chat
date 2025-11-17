#!/usr/bin/env python3
"""MCP Server wrapper with enhanced logging for debugging."""
import sys
import logging
from pathlib import Path

# Configure logging to a file for debugging
log_file = Path(__file__).parent / "mcp_server.log"
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stderr)
    ]
)

logger = logging.getLogger("mcp-wrapper")
logger.info("=== MCP Server Starting ===")
logger.info(f"Python version: {sys.version}")
logger.info(f"Working directory: {Path.cwd()}")
logger.info(f"Log file: {log_file}")

try:
    # Import the main server
    from app.main import main
    import asyncio
    
    logger.info("Starting MCP server...")
    asyncio.run(main())
except Exception as e:
    logger.error(f"Failed to start MCP server: {e}", exc_info=True)
    sys.exit(1)
