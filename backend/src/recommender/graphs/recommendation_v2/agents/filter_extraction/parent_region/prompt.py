from langchain_core.prompts import ChatPromptTemplate

from recommender.graphs.recommendation_v2.filter_models import (
    ALLOWED_RECOMMENDATION_V2_PARENT_REGION_NAMES,
)

allowed_parent_region_values = "\n".join(
    f"- {region_name}" for region_name in ALLOWED_RECOMMENDATION_V2_PARENT_REGION_NAMES
)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            f"""
            You extract broad parent-region (continent-level) filters for the current recommendation_v2 chat turn.

            CRITICAL RULE — READ CAREFULLY:
            Only return parent_regions when the user EXPLICITLY names a continent or large geographic area.
            If the user talks about anything else (vibe, activities, budget, season, food, etc.) without naming a continent-level place, you MUST return null.

            Inputs:
            - current_user_request: the raw user request for this turn

            Allowed parent_region values:
            {allowed_parent_region_values}

            Rules:
            - Use only the current_user_request.
            - NEVER infer a parent_region from vibe, climate, food, language, landmarks, activities, or other indirect hints.
            - NEVER fill parent_regions just because the user mentioned travel or destinations in general.
            - ONLY fill when a concrete continent or large region is explicitly named.
            - If in doubt, return null.
            - Do not invent parent_regions.
            - Do not return values outside the allowed list.
            - Do not return season, month, budget, price, or activity filters.
            - Return only the `parent_regions` field.
            - Each entry must have name (the parent_region name) and type ("include" or "exclude").
            - Use type="include" when the user wants that parent region.
            - Use type="exclude" when the user rules that parent region out.

            Examples:

            current_user_request: "I want to go to Europe, maybe Spain or Italy"
            parent_regions: [{{{{"name": "Europe", "type": "include"}}}}]

            current_user_request: "Anywhere except Asia"
            parent_regions: [{{{{"name": "Asia", "type": "exclude"}}}}]

            current_user_request: "Somewhere in South America"
            parent_regions: [{{{{"name": "South America", "type": "include"}}}}]

            current_user_request: "beach destination in Australia"
            parent_regions: [{{{{"name": "Australia", "type": "include"}}}}]

            current_user_request: "A safari in Africa"
            parent_regions: [{{{{"name": "Africa", "type": "include"}}}}]

            current_user_request: "I want both Europe and Australia"
            parent_regions: [{{{{"name": "Europe", "type": "include"}}}}, {{{{ "name": "Australia", "type": "include"}}}}]

            current_user_request: "I want Europe but definitely not Asia"
            parent_regions: [{{{{"name": "Europe", "type": "include"}}}}, {{{{ "name": "Asia", "type": "exclude"}}}}]

            current_user_request: "A trip to the USA, maybe the Grand Canyon"
            parent_regions: [{{{{"name": "North America", "type": "include"}}}}]

            --- These must return null (no continent explicitly named) ---

            current_user_request: "I want to go to Japan"
            parent_regions: null

            current_user_request: "I want beaches, good food, and a quiet vibe"
            parent_regions: null

            current_user_request: "Same vibe, but cheaper and near the beach"
            parent_regions: null

            current_user_request: "I want to see safari"
            parent_regions: null

            current_user_request: "I would like to explore mountians with penguins"
            parent_regions: null

            current_user_request: "Show me something romantic and warm"
            parent_regions: null

            current_user_request: "I want a quiet hiking trip in October"
            parent_regions: null

            current_user_request: "luxury tropical destination under 400 a week"
            parent_regions: null
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
