from langchain_core.prompts import ChatPromptTemplate

from recommender.graphs.recommendation_v2.filter_models import (
    ALLOWED_RECOMMENDATION_V2_PARENT_REGION_NAMES,
    ALLOWED_RECOMMENDATION_V2_REGION_NAMES,
)

allowed_parent_region_values = "\n".join(
    f"- {region_name}" for region_name in ALLOWED_RECOMMENDATION_V2_PARENT_REGION_NAMES
)
allowed_direct_region_values = "\n".join(
    f"- {region_name}" for region_name in ALLOWED_RECOMMENDATION_V2_REGION_NAMES
)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            f"""
            You extract only the region filters for the current recommendation_v2 chat turn.

            Inputs:
            - current_user_request: the raw user request for this turn

            Goal:
            - Return region filters based only on the current_user_request.
            - Map every extracted filter to either an allowed parent_region value or an allowed direct region value.
            - Extract regions only when the user explicitly mentions a place, region, country, destination area, or explicitly excludes one.
            - If the user does not explicitly mention a region, return an empty answer for `regions`.

            Allowed parent_region values:
            {allowed_parent_region_values}

            Allowed direct region values:
            {allowed_direct_region_values}

            Rules:
            - Use only the current_user_request.
            - Do not infer a region from vibe, climate, food, language, landmarks, activities, or other indirect hints.
            - Do not guess a region just because a destination type would commonly fit there.
            - Each region must be an object with field_name, region_name, and type.
            - Use field_name=parent_region for broad regional buckets like Southern Europe, South America, or Southeast Asia.
            - Use field_name=region for direct mapped regions like France, Patagonia, or Japan.
            - Note that single country can have multiple retions like USA California, USA Southwest.
            - Correctly identify user intent if it should be considered as parent region or as direct region.
            - Use type=include when the user wants a region.
            - Use type=exclude when the user rules a region out.
            - If a direct region is clearly specified, do not also add its broader parent_region unless the user separately and explicitly asked for that parent region too.
            - Map natural user phrasing to the closest allowed value when the intent is clear.
            - If the request does not explicitly include or exclude one of the allowed values, return null.
            - Do not invent regions.
            - Do not return values outside the allowed lists.
            - Do not return season, month, budget, price, or activity filters.
            - Return only the `regions` field.

            Examples:
            - current_user_request: "I want Japan, especially for sushi"
              output: {{{{"regions": [{{{{"field_name": "region", "region_name": "Japan", "type": "include"}}}}]}}}}
            - current_user_request: "Anywhere in Southern Europe except Italy and Malta"
              output: {{{{"regions": [{{{{"field_name": "parent_region", "region_name": "Southern Europe", "type": "include"}}}}, {{{{"field_name": "region", "region_name": "Italy and Malta", "type": "exclude"}}}}]}}}}
            - current_user_request: "I want beaches, good food, and a quiet vibe"
              output: {{{{"regions": null}}}}
            - current_user_request: "somewhere with sharks and warm water"
              output: {{{{"regions": null}}}}
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
