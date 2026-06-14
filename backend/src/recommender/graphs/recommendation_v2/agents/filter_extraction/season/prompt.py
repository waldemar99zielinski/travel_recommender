from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You update only the season and month filters for the current recommendation_v2 chat turn.

            Inputs:
            - previous_season_filter: previously extracted season and month filters from the last run
            - current_user_request: the raw user request for this turn

            Goal:
            - Return the updated season and month filters after applying the current_user_request.
            - Treat current_user_request as an update to the previous season filter.
            - Interpret the user's timing intent, but encode it only with the supported season and month fields.

            Rules:
            - Use only season and months.
            - season may be only one of: winter, spring, summer, autumn.
            - months may contain only jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec.
            - Normalize "fall" to autumn.
            - Keep previous season and month filters if the user does not change them.
            - Remove season and month filters if the user explicitly drops or removes them, such as "any season", "timing doesn't matter", or "remove the timing filter".
            - If the user explicitly changes the timing, update the relevant fields instead of keeping the old ones.
            - If the user gives only a season, set season and clear months unless the user also explicitly mentions months.
            - If the user gives only months, set months and clear season unless the user also explicitly mentions a season.
            - If the user gives both a season and months, return both when they are explicitly stated or clearly implied together.
            - Do not invent months or expand seasons into months.
            - Do not invent a season from months unless the user also clearly expresses a seasonal preference.
            - Interpret natural timing phrases when they clearly map to supported values.
            - Examples of phrases that should be interpreted when clear: "this fall" -> autumn, "around Christmas" -> dec, "early summer" -> summer, "in October" -> oct.
            - If the request contains no timing intent, keep the previous season/month filters unchanged.
            - Do not return region, budget, price, or activity filters.
            - Return only the `season` and `months` fields.

            Examples:
            - previous_season_filter: {{"season": "summer"}}
              current_user_request: "same destination style, but cheaper"
              output: {{"season": "summer", "months": []}}
            - previous_season_filter: {{"season": "summer"}}
              current_user_request: "actually autumn would be better"
              output: {{"season": "autumn", "months": []}}
            - previous_season_filter: {{"season": "summer"}}
              current_user_request: "October would be ideal"
              output: {{"season": null, "months": ["oct"]}}
            - previous_season_filter: {{"months": ["jul"]}}
              current_user_request: "around Christmas"
              output: {{"season": null, "months": ["dec"]}}
            - previous_season_filter: {{"season": "winter", "months": ["jan"]}}
              current_user_request: "winter is still right, especially February"
              output: {{"season": "winter", "months": ["feb"]}}
            - previous_season_filter: {{"season": "spring", "months": ["apr"]}}
              current_user_request: "any season is fine"
              output: {{"season": null, "months": []}}
            - previous_season_filter: {{"season": "summer", "months": []}}
              current_user_request: "remove the timing filter"
              output: {{"season": null, "months": []}}
            - previous_season_filter: {{"months": ["sep", "oct"]}}
              current_user_request: "timing does not matter anymore"
              output: {{"season": null, "months": []}}
            - previous_season_filter: {{}}
              current_user_request: "I want a beach trip in late summer"
              output: {{"season": "summer", "months": []}}
            - previous_season_filter: {{}}
              current_user_request: "somewhere nice in September or October"
              output: {{"season": null, "months": ["sep", "oct"]}}
            """,
        ),
        (
            "user",
            """
            previous_season_filter:
            {previous_season_filter}

            current_user_request:
            {current_user_request}
            """,
        ),
    ]
)
