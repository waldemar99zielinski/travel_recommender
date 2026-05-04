from __future__ import annotations

import json
import os

from openai import OpenAI

from region_description_generation.context import RegionResearchContext
from region_description_generation.context import SYSTEM_PROMPT_TEMPLATE


class RegionDescriptionGenerationAgent:
    """Web-search-backed agent that generates a detailed description per region."""

    def __init__(
        self,
        *,
        model: str,
        search_tool: str,
        search_context_size: str,
        temperature: float,
        max_output_tokens: int,
    ) -> None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required for description generation.")

        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.search_tool = search_tool
        self.search_context_size = search_context_size
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens

    def generate_description(
        self,
        *,
        context: RegionResearchContext,
        catalog_summary: str,
    ) -> str:
        """Generate one detailed embedding description for a region."""
        response = self.client.responses.create(
            model=self.model,
            instructions=SYSTEM_PROMPT_TEMPLATE.format(catalog_summary=catalog_summary),
            input=json.dumps(context.to_prompt_payload(), ensure_ascii=False, indent=2),
            tools=[
                {
                    "type": self.search_tool,
                    "search_context_size": self.search_context_size,
                }
            ],
            text={"verbosity": "high"},
            max_output_tokens=self.max_output_tokens,
            temperature=self.temperature,
            parallel_tool_calls=False,
        )

        description = response.output_text.strip()
        if not description:
            raise ValueError(f"No text response returned for destination {context.destination_id}")
        if len(description) < 400:
            raise ValueError(
                f"Generated description for {context.destination_id} is too short to be useful for embeddings."
            )
        return description
