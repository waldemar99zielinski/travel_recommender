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
            - Always return all three fields: `filter_removed`, `season`, and `months`.

            Rules:
            - Use only season and months.
            - Set filter_removed=true only when current_user_request explicitly says to remove, clear, drop, reset, ignore, or stop using all filters/constraints, or explicitly says to remove, clear, drop, reset, ignore, or stop using the season, month, timing, weather, or date filter specifically.
            - Do not set filter_removed=true for vague preference changes, such as "different time", "more flexible", "less strict", "show more options", or "not that important", unless the user explicitly mentions removing all filters or removing the timing-related filter.
            - If current_user_request explicitly removes all filters/constraints, output exactly: {{"filter_removed": true, "season": null, "months": []}}.
            - If current_user_request explicitly removes the timing-related filter, output exactly: {{"filter_removed": true, "season": null, "months": []}}.
            - Do not keep a previous season or previous months after an explicit timing or all-filter removal request.
            - If no seasonality filter is explicitly removed, set filter_removed=false.
            - season may be only one of: winter, spring, summer, autumn.
            - months may contain only jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec.
            - Normalize "fall" to autumn.
            - Keep previous season and month filters if the user does not change them.
            - Remove season and month filters if the user explicitly drops, clears, or removes them, such as "any season", "timing doesn't matter", "remove the timing filter", or "drop the summer filter".
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
              output: {{"filter_removed": true, "season": null, "months": []}}
            - previous_season_filter: {{"season": "summer", "months": []}}
              current_user_request: "remove the timing filter"
              output: {{"filter_removed": true, "season": null, "months": []}}
            - previous_season_filter: {{"season": "summer", "months": []}}
              current_user_request: "drop the summer filter"
              output: {{"filter_removed": true, "season": null, "months": []}}
            - previous_season_filter: {{"season": "summer", "months": ["jul"]}}
              current_user_request: "remove all filters"
              output: {{"filter_removed": true, "season": null, "months": []}}
            - previous_season_filter: {{"season": "winter", "months": ["jan"]}}
              current_user_request: "clear every filter and show me anything"
              output: {{"filter_removed": true, "season": null, "months": []}}
            - previous_season_filter: {{"months": ["sep", "oct"]}}
              current_user_request: "reset all constraints"
              output: {{"filter_removed": true, "season": null, "months": []}}
            - previous_season_filter: {{"months": ["sep", "oct"]}}
              current_user_request: "timing does not matter anymore"
              output: {{"season": null, "months": []}}
            - previous_season_filter: {{}}
              current_user_request: "I want a beach trip in late summer"
              output: {{"season": "summer", "months": []}}
            - previous_season_filter: {{}}
              current_user_request: "somewhere nice in September or October"
              output: {{"season": null, "months": ["sep", "oct"]}}
            - previous_season_filter: {{"season": "summer", "months": []}}
              current_user_request: "show me more flexible options"
              output: {{"filter_removed": false, "season": "summer", "months": []}}
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
