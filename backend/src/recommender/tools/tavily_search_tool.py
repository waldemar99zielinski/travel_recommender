from __future__ import annotations

from typing import Any

from langchain_core.tools import StructuredTool
from tavily import TavilyClient

from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


class InternetSearchTool:
    """Injectable web search tool backed by the Tavily API.

    Usage:
        tool = InternetSearchTool(api_key="...")
        formatted = tool.search("things to do in Paris", limit=10)
    """

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._client: TavilyClient | None = None

    def search(
        self,
        query: str,
        limit: int = 10,
        include_images: bool = True,
    ) -> str:
        """Search the web and return ``[N]``-prefixed formatted results.

        Args:
            query: Natural language search query.
            limit: Maximum number of search results to return (default 10).
            include_images: Whether to include image results (default True).

        Returns:
            Formatted string with ``[N]``-prefixed results for inclusion
            in an LLM prompt.
        """
        if self._client is None:
            self._client = TavilyClient(api_key=self._api_key)

        raw = self._client.search(
            query=query,
            search_depth="advanced",
            max_results=limit,
            include_images=include_images,
        )
        raw_results: list[dict[str, Any]] = raw.get("results", [])
        raw_images: list[str] = raw.get("images", [])

        if not raw_results:
            return "No search results found."

        lines: list[str] = []
        for i, r in enumerate(raw_results, 1):
            title = r.get("title", "Untitled")
            content = r.get("content", "")
            url = r.get("url", "")
            lines.append(f"[{i}] Source: {title}\n   {content[:300]}\n   URL: {url}")

        if raw_images:
            img_start = len(raw_results) + 1
            for j, img_url in enumerate(raw_images, img_start):
                lines.append(f"[{j}] Image: {img_url}")

        return "\n\n".join(lines)


def create_tavily_search_tool(api_key: str) -> StructuredTool:
    """Create a LangChain-compatible Tavily search tool."""
    search_tool = InternetSearchTool(api_key=api_key)

    def tavily_search(query: str, limit: int = 5, include_images: bool = True) -> str:
        """Search the public web using Tavily and return formatted results."""
        logger.info(
            "tavily_search called with query=%s limit=%s include_images=%s",
            query,
            limit,
            include_images,
        )
        return search_tool.search(
            query=query,
            limit=limit,
            include_images=include_images,
        )

    return StructuredTool.from_function(
        func=tavily_search,
        name="tavily_search",
        description=(
            "Search the public web for recent or external information and return "
            "formatted source snippets and URLs."
        ),
    )
