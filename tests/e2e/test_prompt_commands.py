"""`/command doc_id` in the CLI chat: CliChat fetches the MCP prompt and Claude carries it out with the tools."""

import asyncio

from anthropic.types import TextBlock

from core.cli_chat import CliChat
from mcp_client import MCPClient
from tests.e2e.scripted_claude import ScriptedClaude, assistant_message, tool_use
from tests.support import connect_to_server


def test_client_lists_the_server_prompts() -> None:
    async def scenario() -> list[str]:
        async with connect_to_server() as client:
            prompts = await client.list_prompts()

            return sorted(prompt.name for prompt in prompts)

    assert asyncio.run(scenario()) == ["format", "summarize"]


def test_format_command_sends_the_prompt_and_edits_through_the_tool() -> None:
    edit_input = {"doc_id": "plan.md", "old_str": "The plan", "new_str": "# Plan\n\nThe plan"}
    replies = [
        assistant_message([tool_use("toolu_1", "edit_document", edit_input)], "tool_use"),
        assistant_message([TextBlock(type="text", text="# Plan")], "end_turn"),
    ]
    claude = ScriptedClaude(replies)

    async def scenario() -> tuple[str, str]:
        async with connect_to_server() as client:
            chat = CliChat(doc_client=client, clients={"doc_client": client}, claude_service=claude)
            await chat.run("/format plan.md")
            first_message = chat.messages[0]["content"]

            return first_message, await read_plan(client)

    first_message, plan = asyncio.run(scenario())

    assert "reformat a document to be written with markdown syntax" in first_message
    assert "plan.md" in first_message
    assert plan.startswith("# Plan\n\nThe plan outlines")


async def read_plan(client: MCPClient) -> str:
    return await client.read_resource("docs://documents/plan.md")


def test_summarize_command_reads_the_document_through_the_tool() -> None:
    read_request = tool_use("toolu_1", "read_doc_contents", {"doc_id": "financials.docx"})
    replies = [
        assistant_message([read_request], "tool_use"),
        assistant_message([TextBlock(type="text", text="- Budget and expenditures")], "end_turn"),
    ]
    claude = ScriptedClaude(replies)

    async def scenario() -> tuple[str, str]:
        async with connect_to_server() as client:
            chat = CliChat(doc_client=client, clients={"doc_client": client}, claude_service=claude)
            answer = await chat.run("/summarize financials.docx")

            return chat.messages[0]["content"], answer

    first_message, answer = asyncio.run(scenario())

    assert "Your goal is to summarize a document." in first_message
    assert "financials.docx" in first_message
    assert "budget and expenditures" in claude.tool_results[0]["content"]
    assert answer == "- Budget and expenditures"
