import asyncio
import json

import pytest
from mcp import types
from mcp.shared.exceptions import McpError
from pydantic import AnyUrl

from tests.support import BINARY_RESOURCE_SERVER_SCRIPT, connect_to_server

DOC_IDS = ["deposition.md", "report.pdf", "financials.docx", "outlook.pdf", "plan.md", "spec.txt"]


def read_raw(uri: str) -> types.TextResourceContents:
    async def scenario() -> types.TextResourceContents:
        async with connect_to_server() as client:
            result = await client.session().read_resource(AnyUrl(uri))
            contents = result.contents[0]
            assert isinstance(contents, types.TextResourceContents)

            return contents

    return asyncio.run(scenario())


def test_server_lists_the_direct_and_templated_resources() -> None:
    async def scenario() -> tuple[list[str], list[str]]:
        async with connect_to_server() as client:
            resources = await client.session().list_resources()
            templates = await client.session().list_resource_templates()

            return [str(r.uri) for r in resources.resources], [t.uriTemplate for t in templates.resourceTemplates]

    uris, templates = asyncio.run(scenario())

    assert uris == ["docs://documents"]
    assert templates == ["docs://documents/{doc_id}"]


def test_document_list_is_json_with_every_doc_id() -> None:
    contents = read_raw("docs://documents")

    assert contents.mimeType == "application/json"
    assert json.loads(contents.text) == DOC_IDS


def test_document_resource_returns_its_text() -> None:
    contents = read_raw("docs://documents/deposition.md")

    assert contents.mimeType == "text/plain"
    assert contents.text == "This deposition covers the testimony of Angela Smith, P.E."


def read_parsed(uri: str) -> object:
    async def scenario() -> object:
        async with connect_to_server() as client:
            return await client.read_resource(uri)

    return asyncio.run(scenario())


def test_client_parses_the_json_document_list() -> None:
    assert read_parsed("docs://documents") == DOC_IDS


def test_client_returns_plain_text_documents_as_strings() -> None:
    assert read_parsed("docs://documents/plan.md") == "The plan outlines the steps for the project's implementation."


def test_unknown_document_resource_is_an_error() -> None:
    with pytest.raises(McpError, match="missing.md not found"):
        read_raw("docs://documents/missing.md")


def test_client_refuses_a_binary_resource() -> None:
    async def scenario() -> None:
        async with connect_to_server(BINARY_RESOURCE_SERVER_SCRIPT) as client:
            await client.read_resource("files://logo.png")

    with pytest.raises(ValueError, match="files://logo.png is not text"):
        asyncio.run(scenario())
