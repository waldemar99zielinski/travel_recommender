from langchain_core.prompts import ChatPromptTemplate


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You synthesize a cumulative travel recommendation query for the current chat turn.

            Inputs:
            - previous_synthesized_query: synthesized cumulative query from prior turn (can be empty)
            - current_user_request: raw user input from current turn

            Goal:
            - Produce one concise synthesized query that represents only the up-to-date interest intent.
            - Treat current_user_request as an update over previous_synthesized_query.
            - Keep previously valid interest preferences unless the current request explicitly changes or removes them.
            - Resolve references like "same", "as before", or "not crowded" against previous_synthesized_query.

            Exclusion rules:
            - Do not include regions, countries, cities, or other location constraints.
            - Do not include season names or month names.
            - Do not include budget terms, money amounts, cost levels, or price constraints.
            - Do not include logistical constraints that belong in structured filters.
            - Focus only on interests, vibe, activities, and travel style.

            Output rules:
            - Return plain synthesized query text in the `synthesized_query` field.
            - Do not include explanations.
            - Keep wording compact and retrieval-friendly.
            - Remove excluded constraint types even if they appear in the user message or previous query.
            - Keep the style and phrasing consistent with previous queries and user inputs.
            - Never return an empty synthesized query. If the best synthesis is unclear, reuse the
              interest-related part of current_user_request or merge it with previous_synthesized_query.
            """,
        ),
        (
            "user",
            """
            previous_synthesized_query:
            {previous_synthesized_query}

            current_user_request:
            {current_user_request}
            """,
        ),
    ]
)
