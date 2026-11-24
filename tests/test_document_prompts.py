import asyncio

import pytest
from mcp import types

from tests.support import connect_to_server


def get_raw_prompt(name: str, doc_id: str) -> types.GetPromptResult:
    async def scenario() -> types.GetPromptResult:
        async with connect_to_server() as client:
            return await client.session().get_prompt(name, {"doc_id": doc_id})

    return asyncio.run(scenario())


def test_server_lists_both_prompts_with_a_doc_id_argument() -> None:
    async def scenario() -> list[types.Prompt]:
        async with connect_to_server() as client:
            result = await client.session().list_prompts()

            return result.prompts

    prompts = asyncio.run(scenario())

    assert sorted(prompt.name for prompt in prompts) == ["format", "summarize"]
    assert all([argument.name for argument in prompt.arguments or []] == ["doc_id"] for prompt in prompts)


@pytest.mark.parametrize(
    ("name", "tool_name"),
    [("format", "edit_document"), ("summarize", "read_doc_contents")],
)
def test_prompt_is_one_user_message_with_the_doc_id_and_its_tool(name: str, tool_name: str) -> None:
    messages = get_raw_prompt(name, "plan.md").messages

    assert len(messages) == 1
    assert messages[0].role == "user"
    assert isinstance(messages[0].content, types.TextContent)
    assert "<document_id>\n    plan.md\n    </document_id>" in messages[0].content.text
    assert tool_name in messages[0].content.text
