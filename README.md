# MCP Document Chat

Code for Anthropic Academy's [Introduction to Model Context Protocol](https://academy.claude.com/courses/introduction-to-model-context-protocol/defining-tools-with-mcp) course, built on its starter `cli_project`.

## Course progress

- [x] Defining tools with MCP: `read_doc_contents` and `edit_document` in `mcp_server.py`
- [x] Implementing a client: `list_tools` and `call_tool` in `mcp_client.py`
- [x] Defining resources: `docs://documents` and `docs://documents/{doc_id}` in `mcp_server.py`
- [x] Accessing resources: `read_resource` in `mcp_client.py`
- [ ] Defining prompts: `/format` and summarize in `mcp_server.py`
- [ ] Prompts in the client: `list_prompts` and `get_prompt` in `mcp_client.py`

Each lesson is one commit. The remaining `TODO`s in the code mark the lessons still to do.

## Quick checks

```bash
uv run pytest           # starts the server over stdio and calls the tools through MCPClient
uv run mcp_client.py    # prints the tools the server exposes
uv run mcp dev mcp_server.py   # MCP Inspector (needs Node.js)
```

MCP Chat is a command-line interface application that enables interactive chat capabilities with AI models through the Anthropic API. The application supports document retrieval, command-based prompts, and extensible tool integrations via the MCP (Model Context Protocol) architecture.

## Docker

Everything the project needs (Python 3.13, uv, the locked dependencies, Node.js 22 and the MCP Inspector) is in the
image, so the host needs only Docker.

```bash
docker compose run --rm test        # unit + e2e tests, no API key needed
docker compose run --rm chat        # the chat; reads ANTHROPIC_API_KEY and CLAUDE_MODEL from .env
docker compose up inspector         # MCP Inspector on http://localhost:6274 (open the URL it prints, with the token)
```

The live API test is opt-in because it costs money:
`docker compose run --rm -e RUN_LIVE_TESTS=1 -e ANTHROPIC_API_KEY test`.

The inspector refuses to listen on all interfaces, so its service uses `network_mode: host` and stays on loopback. On
Docker Desktop that only reaches your machine when **Settings → Resources → Network → Enable host networking** is on.

## Tests

- `tests/test_document_tools.py`: starts the server over stdio and calls each tool through `MCPClient`.
- `tests/e2e/test_chat_tool_loop.py`: runs the real chat loop (`Chat` → `ToolManager` → `MCPClient` → server) with a
  scripted Claude in place of the API.
- `tests/e2e/test_live_claude.py`: the same loop against the real API, skipped unless `RUN_LIVE_TESTS=1`.

## Prerequisites

- Python 3.10 to 3.13
- Anthropic API Key

## Setup

### Step 1: Configure the environment variables

1. Copy `.env.example` to `.env` (`cp .env.example .env`) and verify that the following variables are set correctly:

```
ANTHROPIC_API_KEY=""  # Enter your Anthropic API secret key
```

### Step 2: Install dependencies

#### Option 1: Setup with uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver.

1. Install uv, if not already installed:

```bash
pip install uv
```

2. Create and activate a virtual environment:

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
uv pip install -e .
```

4. Run the project

```bash
uv run main.py
```

#### Option 2: Setup without uv

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies, and set `USE_UV=0` in the `.env` file:

```bash
pip install "anthropic<1" python-dotenv prompt-toolkit "mcp[cli]>=1.8.0,<2" "certifi==2026.10.18"
```

3. Run the project

```bash
python main.py
```

## Usage

### Basic Interaction

Simply type your message and press Enter to chat with the model.

### Document Retrieval

Use the @ symbol followed by a document ID to include document content in your query:

```
> Tell me about @deposition.md
```

### Commands

Use the / prefix to execute commands defined in the MCP server:

```
> /format deposition.md
```

Commands will auto-complete when you press Tab.

## Development

### Adding New Documents

Edit the `mcp_server.py` file to add new documents to the `docs` dictionary.

### Implementing MCP Features

To fully implement the MCP features:

1. Complete the TODOs in `mcp_server.py`
2. Implement the missing functionality in `mcp_client.py`

### Tests

```bash
uv run pytest
```
