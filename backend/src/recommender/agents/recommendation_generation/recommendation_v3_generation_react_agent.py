from __future__ import annotations

from typing import Any

from langgraph.prebuilt import create_react_agent

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool

from recommender.agents.recommendation_generation.recommendation_v3_generation_react_prompt import (
    recommendation_v3_generation_react_prompt,
)
from recommender.agents.recommendation_generation.recommendation_v3_generation_tools import (
    SearchResultsContainer,
    create_search_tool,
)
from recommender.models.llm.llm import create_llm_chat_model
from recommender.models.llm.llm_config import LLMConfig
from storage.stores.search_models import ScoredTravelDestination
from storage.stores.travel_destination_store import TravelDestinationStore


class RecommendationV3ReActGenerationAgent:
    """ReAct agent that searches travel destinations via tool calling."""

    def __init__(
        self,
        llm: BaseChatModel,
        search_tool: BaseTool,
        result_container: SearchResultsContainer,
        prompt: Any = None,
    ) -> None:
        self._result_container = result_container
        self._agent = create_react_agent(
            model=llm,
            tools=[search_tool],
            prompt=prompt or recommendation_v3_generation_react_prompt,
        )

    def invoke(self, synthesized_query: str) -> list[ScoredTravelDestination]:
        self._result_container.recommendations = []
        self._agent.invoke({"messages": [("human", synthesized_query)]})
        return self._result_container.recommendations

    @classmethod
    def builder(
        cls,
        travel_destination_store: TravelDestinationStore,
    ) -> RecommendationV3ReActGenerationAgentBuilder:
        return RecommendationV3ReActGenerationAgentBuilder(travel_destination_store)


class RecommendationV3ReActGenerationAgentBuilder:

    def __init__(self, travel_destination_store: TravelDestinationStore) -> None:
        self._store = travel_destination_store
        self._llm: BaseChatModel | None = None
        self._prompt: Any = None

    def with_llm(self, llm: BaseChatModel) -> RecommendationV3ReActGenerationAgentBuilder:
        self._llm = llm
        return self

    def with_prompt(self, prompt: Any) -> RecommendationV3ReActGenerationAgentBuilder:
        self._prompt = prompt
        return self

    def build(self) -> RecommendationV3ReActGenerationAgent:
        result_container = SearchResultsContainer()
        search_tool: BaseTool = create_search_tool(self._store, result_container)
        llm = self._llm or create_llm_chat_model(LLMConfig())
        return RecommendationV3ReActGenerationAgent(
            llm=llm,
            search_tool=search_tool,
            result_container=result_container,
            prompt=self._prompt,
        )
