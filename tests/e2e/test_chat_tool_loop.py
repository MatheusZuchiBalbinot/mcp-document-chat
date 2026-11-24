"""Drives the real chat loop end to end: Chat -> ToolManager -> MCPClient -> mcp_server.py over stdio.

Only Claude is replaced, by a scripted stand-in that asks for tools the way the API would, so the test is free and
needs no API key.
"""

import asyncio

from anthropic.types import Message, TextBlock, ToolUseBlock, Usage

from core.chat import Chat
from core.claude import Claude
from tests.support import connect_to_server


def assistant_message(content: list, stop_reason: str) -> Message:
    usage = Usage(input_tokens=0, output_tokens=0)

    return Message(
        id="msg_scripted",
        type="message",
        role="assistant",
        model="scripted",
        content=content,
        stop_reason=stop_reason,
        stop_sequence=None,
        usage=usage,
    )


def tool_use(tool_use_id: str, name: str, tool_input: dict) -> ToolUseBlock:
    return ToolUseBlock(id=tool_use_id, type="tool_use", name=name, input=tool_input)


class ScriptedClaude(Claude):
    """Replays fixed replies and records what the chat loop sent back."""

    def __init__(self, replies: list[Message]) -> None:
        self.model = "scripted"
        self._replies = list(replies)
        self.offered_tools: list[str] = []
        self.tool_results: list[dict] = []

    def chat(self, messages, system=None, temperature=1.0, stop_sequences=[], tools=None, thinking=False, thinking_budget=1024) -> Message:  # noqa: B006 mirrors Claude.chat
        self.offered_tools = [tool["name"] for tool in tools or []]
        last_content = messages[-1]["content"]

        if isinstance(last_content, list):
            self.tool_results += [part for part in last_content if part.get("type") == "tool_result"]

        return self._replies.pop(0)


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
