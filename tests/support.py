import sys
from pathlib import Path

from mcp.types import CallToolResult, TextContent

from mcp_client import MCPClient

TESTS_DIR = Path(__file__).resolve().parent
SERVER_SCRIPT = str(TESTS_DIR.parent / "mcp_server.py")
BINARY_RESOURCE_SERVER_SCRIPT = str(TESTS_DIR / "servers" / "binary_resource_server.py")


def connect_to_server(script: str = SERVER_SCRIPT) -> MCPClient:
    """A client for a fresh server process, so each test starts from the original documents."""
    return MCPClient(command=sys.executable, args=[script])


def result_text(result: CallToolResult) -> str:
    return "".join(item.text for item in result.content if isinstance(item, TextContent))
