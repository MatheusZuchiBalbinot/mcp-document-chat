"""`@doc_id` mentions in the CLI chat: CliChat reads the documents through MCP resources and puts them in the prompt."""

import asyncio

from core.cli_chat import CliChat
from tests.e2e.scripted_claude import ScriptedClaude
from tests.support import connect_to_server


def process_query(query: str) -> str:
    async def scenario() -> str:
        async with connect_to_server() as client:
            chat = CliChat(doc_client=client, clients={"doc_client": client}, claude_service=ScriptedClaude([]))
            await chat._process_query(query)

            return chat.messages[-1]["content"]

    return asyncio.run(scenario())


def test_mentioned_document_is_inlined_in_the_prompt() -> None:
    prompt = process_query("Tell me about @report.pdf")

    assert '<document id="report.pdf">' in prompt
    assert "20m condenser tower" in prompt


def test_unmentioned_documents_stay_out_of_the_prompt() -> None:
    prompt = process_query("Tell me about @report.pdf")

    assert "deposition.md" not in prompt
