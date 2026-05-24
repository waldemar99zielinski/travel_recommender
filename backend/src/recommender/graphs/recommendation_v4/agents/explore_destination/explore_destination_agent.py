from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import BasePromptTemplate
from langchain_core.tools import BaseTool
from pydantic import BaseModel
from pydantic import Field

from recommender.agents.base.base_agent import BaseReActAgent
from recommender.agents.base.base_agent import BaseReActAgentBuilder
from recommender.graphs.recommendation_v4.agents.explore_destination.explore_destination_prompt import (
    EXPLORE_DESTINATION_SYSTEM_PROMPT,
)
from recommender.graphs.recommendation_v4.agents.explore_destination.explore_destination_prompt import (
    explore_destination_prompt_template,
)
from recommender.graphs.recommendation_v4.agents.explore_destination.explore_destination_tools import (
    create_internet_search_tool,
)
from recommender.graphs.recommendation_v4.models import ExploreDestinationOutput
from recommender.models.llm.llm import create_llm_chat_model
from recommender.models.llm.llm_config import LLMConfig
from recommender.tools.tavily_search_tool import InternetSearchTool
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


class ExploreDestinationInput(BaseModel):
    region_name: str = Field(..., description="Name of the destination region")
    region_description: str = Field(..., description="General description from our database")
    user_query: str = Field(..., description="What the user is looking for")


class ExploreDestinationAgent(BaseReActAgent):

    def invoke(
        self,
        input: ExploreDestinationInput,
    ) -> ExploreDestinationOutput:
        prompt_inputs = self.prompt.format_messages(
            region_name=input.region_name,
            region_description=input.region_description,
            user_query=input.user_query,
        )
        return super().invoke(prompt_inputs)

    @classmethod
    def builder(cls) -> ExploreDestinationAgentBuilder:
        return ExploreDestinationAgentBuilder()


class ExploreDestinationAgentBuilder(BaseReActAgentBuilder):

    def __init__(self) -> None:
        super().__init__(ExploreDestinationAgent)
        self._search_tool: InternetSearchTool | None = None

    def with_search_tool(
        self, search_tool: InternetSearchTool
    ) -> ExploreDestinationAgentBuilder:
        self._search_tool = search_tool
        return self

    def build(self) -> ExploreDestinationAgent:
        llm = self._llm or create_llm_chat_model(LLMConfig())
        prompt = self._prompt or explore_destination_prompt_template
        output_type = self._output_type or ExploreDestinationOutput

        if self._search_tool is None:
            raise ValueError(
                "An InternetSearchTool is required. Call .with_search_tool(tool) before .build()."
            )

        langchain_tool = create_internet_search_tool(self._search_tool)

        return ExploreDestinationAgent(
            llm=llm,
            prompt=prompt,
            output_type=output_type,
            system_prompt=EXPLORE_DESTINATION_SYSTEM_PROMPT,
            tools=[langchain_tool],
        )
