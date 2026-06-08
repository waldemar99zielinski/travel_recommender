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

            Inputs:
            - current_user_request: the raw user request for this turn

            Goal:
            - Return direct region filters based only on the current_user_request.
            - Map every extracted filter to an allowed direct region value with include or exclude intent.
            - Extract regions only when the user explicitly mentions a specific country, island,
              or named destination area from the allowed list.
            - If the user does not explicitly mention a specific region, return null for `regions`.
            - If you are able to figure out how its mapped to a certain region based on your knowledge do it, otherwise leave empty.

            Allowed direct region values:
            {allowed_direct_region_values}

            Rules:
            - Use only the current_user_request.
            - Do not infer a region from vibe, climate, food, language, landmarks, activities, or other indirect hints.
            - Map natural user phrasing to the closest allowed value when the intent is clear.
            - Generalise country names to the allowed sub-regions that belong to that country. For example:
              "Brazil" → one of: Brazil Central West, Brazil North, Brazil Northeast, Brazil South, Brazil Southeast.
              "USA" or "United States" or "America" → one of: USA Alaska, USA California, USA Florida, USA Great Plains, USA Hawaii, USA Mid-Atlantic, USA Midwest, USA New England, USA Pacific Northwest, USA Rocky Mountains, USA South, USA Southwest, USA Texas.
              Use your knowledge to map the user's mention to the most appropriate sub-region based on context (e.g., "beaches in Brazil" → Brazil Northeast or Brazil Southeast; "skiing in the US" → USA Rocky Mountains).
            - If the request does not explicitly include or exclude one of the allowed values, return null.
            - Do not invent regions.
            - Do not return values outside the allowed list.
            - Do not return season, month, budget, price, or activity filters.
            - Return only the `regions` field.
            - Each entry must have name (the region name) and type ("include" or "exclude").
            - Use type="include" when the user wants that region.
            - Use type="exclude" when the user rules that region out.

            Examples:
            - current_user_request: "I want Japan, especially for sushi"
              regions: [{{{{"name": "Japan", "type": "include"}}}}]
            - current_user_request: "Somewhere like Italy and Malta"
              regions: [{{{{"name": "Italy and Malta", "type": "include"}}}}]
            - current_user_request: "Anywhere in Southern Europe except Italy and Malta"
              regions: [{{{{"name": "Italy and Malta", "type": "exclude"}}}}]
            - current_user_request: "beach destination in Brazil"
              regions: [{{{{"name": "Brazil Northeast", "type": "include"}}}}]
            - current_user_request: "A road trip across the USA"
              regions: [{{{{"name": "USA California", "type": "include"}}}}, {{{{ "name": "USA Midwest", "type": "include"}}}}, {{{{ "name": "USA Texas", "type": "include"}}}}]
            - current_user_request: "National parks in the United States"
              regions: [{{{{"name": "USA Rocky Mountains", "type": "include"}}}}]
            - current_user_request: "beach destination in the Caribbean"
              regions: null
            - current_user_request: "I want beaches, good food, and a quiet vibe"
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
