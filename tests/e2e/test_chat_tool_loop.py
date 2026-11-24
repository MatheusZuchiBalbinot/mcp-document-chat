"""Drives the real chat loop end to end: Chat -> ToolManager -> MCPClient -> mcp_server.py over stdio.

Only Claude is replaced, by a scripted stand-in that asks for tools the way the API would, so the test is free and
needs no API key.
"""

import asyncio

from anthropic.types import TextBlock

from core.chat import Chat
from tests.e2e.scripted_claude import ScriptedClaude, assistant_message, tool_use
from tests.support import connect_to_server


def run_chat(claude: ScriptedClaude, query: str) -> str:
    async def scenario() -> str:
        async with connect_to_server() as client:
            chat = Chat(claude_service=claude, clients={"doc_client": client})

            return await chat.run(query)

    return asyncio.run(scenario())


def test_claude_reads_a_document_through_the_mcp_tool() -> None:
    read_request = tool_use("toolu_1", "read_doc_contents", {"doc_id": "report.pdf"})
    replies = [
        assistant_message([TextBlock(type="text", text="Reading it."), read_request], "tool_use"),
        assistant_message([TextBlock(type="text", text="It covers a 20m condenser tower.")], "end_turn"),
    ]
    claude = ScriptedClaude(replies)

    answer = run_chat(claude, "What is in report.pdf?")

    assert answer == "It covers a 20m condenser tower."
    assert sorted(claude.offered_tools) == ["edit_document", "read_doc_contents"]
    assert claude.tool_results[0]["tool_use_id"] == "toolu_1"
    assert claude.tool_results[0]["is_error"] is False
    assert "20m condenser tower" in claude.tool_results[0]["content"]


def test_claude_edits_then_reads_back_the_change() -> None:
    edit_request = tool_use("toolu_1", "edit_document", {"doc_id": "spec.txt", "old_str": "equipment", "new_str": "pumps"})
    read_request = tool_use("toolu_2", "read_doc_contents", {"doc_id": "spec.txt"})
    replies = [
        assistant_message([edit_request], "tool_use"),
        assistant_message([read_request], "tool_use"),
        assistant_message([TextBlock(type="text", text="Done.")], "end_turn"),
    ]
    claude = ScriptedClaude(replies)

    run_chat(claude, "Replace equipment with pumps in spec.txt")

    assert "technical requirements for the pumps" in claude.tool_results[1]["content"]


def test_unknown_document_comes_back_as_a_tool_error() -> None:
    read_request = tool_use("toolu_1", "read_doc_contents", {"doc_id": "missing.md"})
    replies = [
        assistant_message([read_request], "tool_use"),
        assistant_message([TextBlock(type="text", text="Not found.")], "end_turn"),
    ]
    claude = ScriptedClaude(replies)

    run_chat(claude, "Read missing.md")

    assert claude.tool_results[0]["is_error"] is True
    assert "missing.md not found" in claude.tool_results[0]["content"]
