import json
from groq import AsyncGroq
from app.core.config import get_settings

settings = get_settings()
_groq_client: AsyncGroq | None = None


def _get_client() -> AsyncGroq:
    global _groq_client
    if _groq_client is None:
        _groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY.get_secret_value())
    return _groq_client


async def chat_with_tools(
    messages: list[dict],
    system_prompt: str,
    tools: list | None = None,
    tool_handler=None,
) -> str:
    client = _get_client()

    groq_messages = [{"role": "system", "content": system_prompt}] + messages

    kwargs: dict = {}
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"

    response = await client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=groq_messages,
        **kwargs,
    )

    message = response.choices[0].message

    if message.tool_calls and tool_handler:
        groq_messages.append({
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in message.tool_calls
            ],
        })

        for tool_call in message.tool_calls:
            args = json.loads(tool_call.function.arguments)
            result = await tool_handler(tool_call.function.name, args)
            groq_messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result),
            })

        final = await client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=groq_messages,
        )
        return final.choices[0].message.content or ""

    return message.content or ""
