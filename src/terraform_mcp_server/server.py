from mcp.server.fastmcp import FastMCP
from .config import settings
from .tools.registry_tools import register_registry_tools
from .tools.tfe_tools import register_tfe_tools
from .registry import registry_client
from .tfe import tfe_client
from loguru import logger
import sys

# Create FastMCP instance
mcp = FastMCP(
    "terraform-mcp-server",
    instructions="""The Terraform MCP server provides tools for generating better Terraform code through registry integration and automating workflows via HCP Terraform/Enterprise APIs.

ALWAYS consult the MCP server before generating any Terraform code to retrieve latest provider documentation and constraints."""
)


# Register tools
register_registry_tools(mcp)
register_tfe_tools(mcp)

async def cleanup():
    logger.info("Shutting down...")
    await registry_client.close()
    await tfe_client.close()

def main():
    import click
    import uvicorn
    from starlette.applications import Starlette
    from starlette.routing import Route, Mount
    from mcp.server.sse import SseServerTransport

    @click.group()
    def cli():
        pass

    @cli.command()
    @click.option("--log-level", default=settings.log_level, help="Log level")
    def stdio(log_level):
        """Run the server using stdio transport."""
        logger.remove()
        logger.add(sys.stderr, level=log_level)
        mcp.run(transport="stdio")

    @cli.command()
    @click.option("--port", default=settings.transport_port, help="Port to listen on")
    @click.option("--host", default=settings.transport_host, help="Host to bind to")
    def sse(port, host):
        """Run the server using SSE transport."""
        logger.info(f"Starting SSE server on {host}:{port}")
        
        # FastMCP's run(transport="sse") handles the Starlette app creation
        mcp.run(transport="sse", host=host, port=port)

    # Alias for backward compatibility or matching Go implementation
    @cli.command(name="streamable-http")
    @click.option("--port", default=settings.transport_port, help="Port to listen on")
    @click.option("--host", default=settings.transport_host, help="Host to bind to")
    @click.pass_context
    def streamable_http(ctx, port, host):
        """Start StreamableHTTP server."""
        ctx.forward(sse)

    cli()

if __name__ == "__main__":
    main()
