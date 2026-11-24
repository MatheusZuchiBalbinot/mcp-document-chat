import asyncio

from tests.support import connect_to_server, result_text


def test_server_lists_both_document_tools() -> None:
    async def scenario() -> list[str]:
        async with connect_to_server() as client:
            tools = await client.list_tools()

            return sorted(tool.name for tool in tools)

    assert asyncio.run(scenario()) == ["edit_document", "read_doc_contents"]


def test_read_returns_document_contents() -> None:
    async def scenario() -> str:
        async with connect_to_server() as client:
            result = await client.call_tool("read_doc_contents", {"doc_id": "report.pdf"})

            return result_text(result)

    assert asyncio.run(scenario()) == "The report details the state of a 20m condenser tower."


def test_edit_is_visible_to_a_later_read() -> None:
    async def scenario() -> str:
        async with connect_to_server() as client:
            edit_input = {"doc_id": "plan.md", "old_str": "steps", "new_str": "phases"}
            await client.call_tool("edit_document", edit_input)
            result = await client.call_tool("read_doc_contents", {"doc_id": "plan.md"})

            return result_text(result)

    assert asyncio.run(scenario()) == "The plan outlines the phases for the project's implementation."


def test_unknown_document_is_reported_as_tool_error() -> None:
    async def scenario() -> tuple[bool, str]:
        async with connect_to_server() as client:
            result = await client.call_tool("read_doc_contents", {"doc_id": "missing.md"})

            return result.isError, result_text(result)

    is_error, text = asyncio.run(scenario())

    assert is_error
    assert "missing.md not found" in text
