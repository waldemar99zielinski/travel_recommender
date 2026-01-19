from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Type, Union, Sequence, Optional
from langchain_openai import ChatOpenAI

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import BasePromptTemplate, ChatPromptTemplate
from langchain_core.prompts import BasePromptTemplate
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable

from recommender.models.llm.llm import create_llm_chat_model
from recommender.models.llm.llm_config import LLMConfig

class BaseAgentBuilder:
    """
    A generic builder that can construct any subclass of BaseAgent.
    """
    def __init__(self, target_class: Type['BaseAgent']):
        self._target_class = target_class
        self._llm: Optional[BaseChatModel] = None
        self._prompt: Optional[BasePromptTemplate] = None
        self._output_type: Optional[Type[Any]] = None

    def with_llm(self, llm: BaseChatModel) -> 'BaseAgentBuilder':
        self._llm = llm
        return self

    def with_prompt(self, prompt: BasePromptTemplate) -> 'BaseAgentBuilder':
        self._prompt = prompt
        return self

    def with_output_type(self, output_type: Type[Any]) -> 'BaseAgentBuilder':
        self._output_type = output_type
        return self

    @abstractmethod
    def build(self) -> 'BaseAgent':
        """
        Abstract: Subclasses must implement the logic to combine 
        stored parameters into a concrete Agent instance.
        """
        pass

@dataclass(slots=True)
class BaseAgent(ABC):
    """
    Agent abstraction.
    Renamed from 'Agent' to 'Chain' to reflect that it is linear (no reasoning loop).
    """

    llm: BaseChatModel
    prompt: BasePromptTemplate
    output_type: Type[Any]
    
    # Internal cache for the runnable agent
    _runnable: Runnable = field(init=False, repr=False)

    def __post_init__(self):
        structured_llm = self.llm.with_structured_output(self.output_type)
        self._runnable = structured_llm

    def invoke(self, inputs: Union[Dict[str, Any], Sequence[BaseMessage]]) -> Any:
        """
        Runs the agent.
        Accepts a dictionary of prompt variables OR a list of messages.
        """
        # The agent handles the formatting automatically based on input type
        response = self._runnable.invoke(inputs)
        return response 

    @classmethod
    @abstractmethod
    def builder(cls) -> BaseAgentBuilder:
        """Factory method to get the correct builder."""
        pass
