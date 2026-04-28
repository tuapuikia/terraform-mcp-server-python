import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_client():
    # Define the server parameters
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "terraform-mcp-server"],
        env=None
    )

    print("Starting MCP Client and connecting to server...")
    
    try:
        # Establish the stdio transport
        async with stdio_client(server_params) as (read, write):
            # Create and manage the session
            async with ClientSession(read, write) as session:
                # Initialize the connection
                print("Initializing session...")
                await session.initialize()
                print("Session initialized successfully.")

                # Interact with the server
                print("\nFetching available tools...")
                tools = await session.list_tools()
                
                tool_names = [t.name for t in tools.tools]
                print(f"Found {len(tool_names)} tools:")
                for name in tool_names:
                    print(f" - {name}")
                
                # Check for an expected tool to verify functionality
                if "search_providers" in tool_names:
                    print("\n✅ Server is working correctly! Tools are accessible.")
                else:
                    print("\n❌ Expected tools not found. Server might not be registering them properly.")
                    sys.exit(1)
                    
    except Exception as e:
        print(f"\n❌ Error connecting to server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_client())
