# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:0.13.0 AS uv

FROM python:3.13-slim-bookworm AS app

COPY --from=uv /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    # main.py starts the server with plain `python` when USE_UV=0; the venv is already on PATH.
    USE_UV=0

RUN useradd --create-home --uid 1000 app && install -d -o app -g app /app
WORKDIR /app

# Dependencies first so code edits don't reinstall them.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY --chown=app:app . .
USER app

CMD ["python", "main.py"]

# The MCP Inspector (`mcp dev`) runs on Node.js 22.19+ next to the Python server.
FROM app AS inspector

USER root
COPY --from=node:22-bookworm-slim /usr/local/bin/node /usr/local/bin/node
COPY --from=node:22-bookworm-slim /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -s /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx \
    && npm install --global --no-update-notifier @modelcontextprotocol/inspector@2.16.0
USER app

# The inspector stays on loopback (its safe default); compose shares the host network so the host can reach it.
ENV MCP_AUTO_OPEN_ENABLED=false

# Same as the course's `npx @modelcontextprotocol/inspector mcp run mcp_server.py`, with the pinned install.
CMD ["mcp-inspector", "mcp", "run", "mcp_server.py"]
