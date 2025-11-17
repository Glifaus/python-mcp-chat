"""Simple MCP client for testing the server in terminal."""
import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_mcp_server():
    """Test the MCP server interactively."""
    # Connect to the MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "app.main"],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print("\n🛠️  Available MCP Tools:")
            print("=" * 60)
            for i, tool in enumerate(tools.tools, 1):
                print(f"{i}. {tool.name}")
                print(f"   📝 {tool.description}")
            print("=" * 60)
            
            # Interactive loop
            while True:
                print("\n" + "=" * 60)
                print("Choose an action:")
                print("1. Send a message")
                print("2. Get recent messages")
                print("3. Get channels")
                print("4. Add reaction")
                print("5. Search messages")
                print("6. Get users list")
                print("7. Custom tool call")
                print("0. Exit")
                print("=" * 60)
                
                choice = input("\nYour choice: ").strip()
                
                if choice == "0":
                    print("\n👋 Goodbye!")
                    break
                
                elif choice == "1":
                    name = input("Your name: ").strip()
                    content = input("Message: ").strip()
                    channel = input("Channel (default: general): ").strip() or "general"
                    
                    result = await session.call_tool("send-message", {
                        "name": name,
                        "content": content,
                        "channel": channel
                    })
                    print(f"\n✅ Result: {result.content[0].text}")
                
                elif choice == "2":
                    limit = input("Limit (default: 10): ").strip() or "10"
                    
                    result = await session.call_tool("get-messages", {
                        "limit": int(limit)
                    })
                    print(f"\n📬 Messages:\n{result.content[0].text}")
                
                elif choice == "3":
                    result = await session.call_tool("get-channels", {})
                    print(f"\n📺 Channels:\n{result.content[0].text}")
                
                elif choice == "4":
                    message_id = input("Message ID: ").strip()
                    user_name = input("Your name: ").strip()
                    emoji = input("Emoji (e.g., 👍): ").strip()
                    
                    result = await session.call_tool("add-reaction", {
                        "message_id": int(message_id),
                        "user_name": user_name,
                        "emoji": emoji
                    })
                    print(f"\n✅ Result: {result.content[0].text}")
                
                elif choice == "5":
                    query = input("Search query: ").strip()
                    limit = input("Limit (default: 20): ").strip() or "20"
                    
                    result = await session.call_tool("search-messages", {
                        "query": query,
                        "limit": int(limit)
                    })
                    print(f"\n🔍 Search Results:\n{result.content[0].text}")
                
                elif choice == "6":
                    limit = input("Limit (default: 10): ").strip() or "10"
                    sort_by = input("Sort by (message_count/last_activity, default: message_count): ").strip() or "message_count"
                    
                    result = await session.call_tool("get-users-list", {
                        "limit": int(limit),
                        "sort_by": sort_by
                    })
                    print(f"\n👥 Users:\n{result.content[0].text}")
                
                elif choice == "7":
                    print("\nAvailable tools:")
                    for i, tool in enumerate(tools.tools, 1):
                        print(f"{i}. {tool.name}")
                    
                    tool_name = input("\nTool name: ").strip()
                    args_json = input("Arguments (JSON): ").strip()
                    
                    try:
                        args = json.loads(args_json) if args_json else {}
                        result = await session.call_tool(tool_name, args)
                        print(f"\n✅ Result: {result.content[0].text}")
                    except json.JSONDecodeError:
                        print("\n❌ Invalid JSON format")
                    except Exception as e:
                        print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    print("🚀 Starting MCP Client Test...")
    print("=" * 60)
    try:
        asyncio.run(test_mcp_server())
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)
