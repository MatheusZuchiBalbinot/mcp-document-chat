"""Calls the real Anthropic API. Opt-in because it costs money: RUN_LIVE_TESTS=1 and ANTHROPIC_API_KEY."""

import asyncio
import os

import pytest

from core.chat import Chat
from core.claude import Claude
from tests.support import connect_to_server

DEFAULT_MODEL = "claude-haiku-5-5"

is_live_enabled = os.getenv("RUN_LIVE_TESTS") == "1" and bool(os.getenv("ANTHROPIC_API_KEY"))


@pytest.mark.skipif(not is_live_enabled, reason="set RUN_LIVE_TESTS=1 and ANTHROPIC_API_KEY to call the API")
def test_claude_answers_from_the_document_tool() -> None:
    async def scenario() -> str:
        claude = Claude(model=os.getenv("CLAUDE_MODEL", DEFAULT_MODEL))

        async with connect_to_server() as client:
            chat = Chat(claude_service=claude, clients={"doc_client": client})

            return await chat.run("Use your tools: what is the height of the tower in report.pdf? Answer briefly.")

    assert "20" in asyncio.run(scenario())
