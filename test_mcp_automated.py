"""Automated tests for the MCP server."""
import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run_automated_tests():
    """Run automated tests on the MCP server."""
    print("🧪 Starting Automated MCP Server Tests")
    print("=" * 70)
    
    # Connect to the MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "app.main"],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()
            print("✅ Server initialized successfully\n")
            
            # Test 1: List tools
            print("📋 Test 1: Listing available tools")
            tools = await session.list_tools()
            print(f"   Found {len(tools.tools)} tools:")
            for tool in tools.tools:
                print(f"   - {tool.name}")
            print()
            
            # Test 2: Send a message
            print("📤 Test 2: Sending a message")
            result = await session.call_tool("send-message", {
                "name": "TestBot",
                "content": "Hello from automated test!",
                "channel": "general"
            })
            print(f"   {result.content[0].text}\n")
            
            # Test 3: Get messages
            print("📥 Test 3: Getting recent messages")
            result = await session.call_tool("get-messages", {"limit": 5})
            print(f"   {result.content[0].text}\n")
            
            # Test 4: Get channels
            print("📺 Test 4: Getting channels list")
            result = await session.call_tool("get-channels", {})
            print(f"   {result.content[0].text}\n")
            
            # Test 5: Add reaction
            print("👍 Test 5: Adding reaction to message 1")
            result = await session.call_tool("add-reaction", {
                "message_id": 1,
                "user_name": "TestBot",
                "emoji": "🚀"
            })
            print(f"   {result.content[0].text}\n")
            
            # Test 6: Get message reactions
            print("😊 Test 6: Getting reactions for message 1")
            result = await session.call_tool("get-message-reactions", {
                "message_id": 1
            })
            print(f"   {result.content[0].text}\n")
            
            # Test 7: Search messages
            print("🔍 Test 7: Searching for messages")
            result = await session.call_tool("search-messages", {
                "query": "test",
                "limit": 10
            })
            print(f"   {result.content[0].text}\n")
            
            # Test 8: Get users list
            print("👥 Test 8: Getting users list")
            result = await session.call_tool("get-users-list", {
                "limit": 5,
                "sort_by": "message_count"
            })
            print(f"   {result.content[0].text}\n")
            
            # Test 9: Reply to message
            print("💬 Test 9: Replying to message 1")
            result = await session.call_tool("reply-to-message", {
                "parent_message_id": 1,
                "name": "TestBot",
                "content": "This is a test reply!"
            })
            print(f"   {result.content[0].text}\n")
            
            # Test 10: Get message thread
            print("🧵 Test 10: Getting message thread")
            result = await session.call_tool("get-message-thread", {
                "message_id": 1
            })
            print(f"   {result.content[0].text}\n")
            
            print("=" * 70)
            print("✅ All tests completed successfully!")


if __name__ == "__main__":
    try:
        asyncio.run(run_automated_tests())
    except KeyboardInterrupt:
        print("\n\n👋 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error running tests: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
