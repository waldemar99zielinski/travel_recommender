from langchain_core.prompts import ChatPromptTemplate

from recommender.graphs.recommendation_v2.filter_models import (
    ALLOWED_RECOMMENDATION_V2_REGION_NAMES,
)

allowed_direct_region_values = "\n".join(
    f"- {region_name}" for region_name in ALLOWED_RECOMMENDATION_V2_REGION_NAMES
)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            f"""
            You extract specific direct-region filters for the current recommendation_v2 chat turn.

            CRITICAL RULE — READ CAREFULLY:
            Only return regions when the user EXPLICITLY names a country, island, city, or named destination area.
            If the user talks about anything else (vibe, activities, budget, season, food, etc.) without naming a specific place, you MUST return null.

            Inputs:
            - current_user_request: the raw user request for this turn

            Allowed direct region values:
            {allowed_direct_region_values}

            Rules:
            - Use only the current_user_request.
            - NEVER infer a region from vibe, climate, food, language, landmarks, activities, or other indirect hints.
            - NEVER fill regions just because the user mentioned travel or destinations in general.
            - ONLY fill when a concrete geographic name is explicitly mentioned (country, island, city, or named destination area).
            - If a country is mentioned without a specific sub-region context, use your knowledge to pick the most appropriate sub-region from the allowed list. For example: "Brazil" with beach context → Brazil Northeast; "USA" without specifics → USA California (most commonly visited); "Brazil" without specifics → Brazil Southeast (most populated).
            - If in doubt, return null.
            - Do not invent regions.
            - Do not return values outside the allowed list.
            - Do not return season, month, budget, price, or activity filters.
            - Return only the `regions` field.
            - Each entry must have name (the region name) and type ("include" or "exclude").
            - Use type="include" when the user wants that region.
            - Use type="exclude" when the user rules that region out.

            Examples:

            current_user_request: "I want Japan, especially for sushi"
            regions: [{{{{"name": "Japan", "type": "include"}}}}]

            current_user_request: "Somewhere like Italy and Malta"
            regions: [{{{{"name": "Italy and Malta", "type": "include"}}}}]

            current_user_request: "Anywhere in Southern Europe except Italy and Malta"
            regions: [{{{{"name": "Italy and Malta", "type": "exclude"}}}}]

            current_user_request: "beach destination in Brazil"
            regions: [{{{{"name": "Brazil Northeast", "type": "include"}}}}]

            current_user_request: "A road trip across the USA"
            regions: [{{{{"name": "USA California", "type": "include"}}}}, {{{{ "name": "USA Midwest", "type": "include"}}}}, {{{{ "name": "USA Texas", "type": "include"}}}}]

            current_user_request: "National parks in the United States"
            regions: [{{{{"name": "USA Rocky Mountains", "type": "include"}}}}]

            --- These must return null (no specific place explicitly named) ---

            current_user_request: "beach destination in the Caribbean"
            regions: null

            current_user_request: "I want beaches, good food, and a quiet vibe"
            regions: null

            current_user_request: "Same vibe, but cheaper and near the beach"
            regions: null

            current_user_request: "Show me something romantic and warm"
            regions: null

            current_user_request: "I want a quiet hiking trip in October"
            regions: null

            current_user_request: "luxury tropical destination under 400 a week"
            regions: null
            """,
        ),
        (
            "user",
            """
            current_user_request:
            {current_user_request}
            """,
        ),
    ]
)
