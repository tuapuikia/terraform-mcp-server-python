import asyncio
import sys
import subprocess
from mcp import ClientSession
from mcp.client.sse import sse_client

async def run_client():
    # Start the server in the background
    print("Starting background SSE server on port 8085...")
    server_process = subprocess.Popen(
        ["uv", "run", "terraform-mcp-server", "sse", "--port", "8085"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Give the server a moment to start
    await asyncio.sleep(2)
    
    # Check if process is still running
    if server_process.poll() is not None:
        out, err = server_process.communicate()
        print(f"Server crashed! Exit code: {server_process.returncode}")
        print(f"Stderr: {err.decode('utf-8')}")
        sys.exit(1)
    
    try:
        # FastMCP sse_app uses /sse endpoint by default
        url = "http://127.0.0.1:8085/sse"
        print(f"Connecting to SSE server at {url}...")
        
        async with sse_client(url) as (read, write):
            async with ClientSession(read, write) as session:
                print("Initializing session...")
                await session.initialize()
                print("Session initialized successfully.")
                
                tools = await session.list_tools()
                tool_names = [t.name for t in tools.tools]
                print(f"Found {len(tool_names)} tools:")
                
                if "search_providers" in tool_names:
                    print("\n✅ SSE Server is working correctly! Tools are accessible.")
                else:
                    print("\n❌ Expected tools not found.")
                    sys.exit(1)
                    
    except Exception as e:
        print(f"\n❌ Error connecting to SSE server: {e}")
        out, err = server_process.communicate()
        print(f"Server Stderr: {err.decode('utf-8')}")
        sys.exit(1)
    finally:
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    asyncio.run(run_client())
