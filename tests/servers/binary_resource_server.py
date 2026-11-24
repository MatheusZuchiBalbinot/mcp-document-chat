"""A minimal MCP server with one binary resource, for testing how the client handles non-text contents."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("BinaryResourceMCP", log_level="ERROR")


@mcp.resource("files://logo.png", mime_type="image/png")
def logo() -> bytes:
    return b"\x89PNG\r\n\x1a\n"


if __name__ == "__main__":
    mcp.run(transport="stdio")
