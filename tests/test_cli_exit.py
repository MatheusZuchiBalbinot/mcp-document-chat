import asyncio

import pytest
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput

from core.cli import CliApp
from core.cli_chat import CliChat


class UnusedChat(CliChat):
    """The exit keys end the loop before the chat is ever asked anything."""

    def __init__(self) -> None:
        pass


@pytest.mark.parametrize("key", ["\x04", "\x03"], ids=["ctrl-d", "ctrl-c"])
def test_exit_key_ends_the_cli_without_an_error(key: str) -> None:
    async def scenario() -> None:
        with create_pipe_input() as pipe_input:
            app = CliApp(UnusedChat())
            app.session.app.input = pipe_input
            app.session.app.output = DummyOutput()
            pipe_input.send_text(key)
            await app.run()

    asyncio.run(scenario())
