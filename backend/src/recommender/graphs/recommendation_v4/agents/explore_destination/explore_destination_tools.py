from langchain_core.tools import BaseTool
from langchain_core.tools import tool

from recommender.tools.tavily_search_tool import InternetSearchTool


def create_internet_search_tool(search_tool: InternetSearchTool) -> BaseTool:
    @tool
    def internet_search(
        query: str,
        limit: int = 10,
        include_images: bool = True,
    ) -> str:
        """Search the web for attractions, activities, and points of interest."""
        return search_tool.search(query=query, limit=limit, include_images=include_images)

    return internet_search
