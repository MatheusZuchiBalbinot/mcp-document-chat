"""A scripted stand-in for core.claude.Claude: replays fixed replies so e2e tests need no API key."""

from anthropic.types import Message, ToolUseBlock, Usage

from core.claude import Claude


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
