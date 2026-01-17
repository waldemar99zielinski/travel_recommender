from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Type, Union, Sequence

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import BasePromptTemplate
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable

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
