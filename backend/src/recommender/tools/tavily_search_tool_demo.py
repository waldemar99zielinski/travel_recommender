from __future__ import annotations

import argparse
import json

from langchain.agents import create_agent
from langchain_core.messages import BaseMessage

from recommender.common.configuration import Configuration
from recommender.models.llm.llm import create_llm_chat_model
from recommender.models.llm.llm_config import LLMConfig
from recommender.tools.tavily_search_tool import InternetSearchTool
from recommender.tools.tavily_search_tool import create_tavily_search_tool


def _serialize_messages(messages: list[BaseMessage]) -> str:
    parts: list[str] = []

    for message in messages:
        role = getattr(message, "type", message.__class__.__name__)
        content = getattr(message, "content", "")
        parts.append(f"{role}: {content}")

        tool_calls = getattr(message, "tool_calls", None)
        if tool_calls:
            parts.append(f"tool_calls: {tool_calls}")

    return "\n\n".join(parts)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a simple Tavily-backed demo agent.",
    )
    parser.add_argument(
        "query",
        help="User query to ask the demo agent.",
    )
    parser.add_argument(
        "--direct",
        action="store_true",
        help="Run the Tavily tool directly instead of through an agent.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Maximum number of Tavily results to request.",
    )
    parser.add_argument(
        "--include-images",
        action="store_true",
        help="Include image results in the Tavily response.",
    )
    parser.add_argument(
        "--provider",
        choices=["ollama", "chatgpt"],
        default="ollama",
        help="LLM provider for the demo agent.",
    )
    parser.add_argument(
        "--model",
        default="llama3.1",
        help="LLM model name for the demo agent.",
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help="Optional base URL for the selected LLM provider.",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="Optional API key for the selected LLM provider.",
    )
    return parser


def main() -> None:
    args = _build_arg_parser().parse_args()
    configuration = Configuration()

    if not configuration.tavily_api_key:
        raise ValueError("TAVILY_API_KEY is not configured")

    if args.direct:
        tool = InternetSearchTool(api_key=configuration.tavily_api_key)
        result = tool.search(
            query=args.query,
            limit=args.limit,
            include_images=args.include_images,
        )
        print(result)
        return

    llm = create_llm_chat_model(
        LLMConfig(
            provider=args.provider,
            model=args.model,
            api_key=args.api_key,
            base_url=args.base_url,
        )
    )
    agent = create_agent(
        model=llm,
        tools=[create_tavily_search_tool(configuration.tavily_api_key)],
        system_prompt=(
            "You are a small demo agent that can use the tavily_search tool when "
            "needed. Search the web when the user asks about current, factual, or "
            "external information, then answer concisely and cite the source titles or URLs you used."
        ),
        debug=True,
    )

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": args.query,
                }
            ]
        }
    )

    print("=== Raw Result ===")
    print(json.dumps(result, default=str, indent=2))

    messages = result.get("messages") if isinstance(result, dict) else None
    if isinstance(messages, list):
        print("\n=== Message Transcript ===")
        print(_serialize_messages(messages))


if __name__ == "__main__":
    main()
