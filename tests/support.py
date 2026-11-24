import sys
from pathlib import Path

from mcp.types import CallToolResult, TextContent

from mcp_client import MCPClient

SERVER_SCRIPT = str(Path(__file__).resolve().parent.parent / "mcp_server.py")


def connect_to_server() -> MCPClient:
    """A client for a fresh mcp_server.py process, so each test starts from the original documents."""
    return MCPClient(command=sys.executable, args=[SERVER_SCRIPT])


def result_text(result: CallToolResult) -> str:
    return "".join(item.text for item in result.content if isinstance(item, TextContent))
