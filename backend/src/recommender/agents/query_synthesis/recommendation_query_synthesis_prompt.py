from langchain_core.prompts import ChatPromptTemplate


recommendation_query_synthesis_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You synthesize a cumulative travel recommendation query for the current chat turn.

            Inputs:
            - previous_synthesized_query: synthesized cumulative query from prior turn (can be empty)
            - current_user_request: raw user input from current turn

            Goal:
            - Produce one concise synthesized query that represents the up-to-date recommendation intent.
            - Treat current_user_request as an update over previous_synthesized_query.
            - Keep previously valid constraints unless the current request explicitly changes or removes them.
            - Resolve references like "same", "as before", "change budget", "not crowded" against previous_synthesized_query.

            Output rules:
            - Return plain synthesized query text in the `synthesized_query` field.
            - Do not include explanations.
            - Keep wording compact and retrieval-friendly.
            - Keep the style and phrasing consistent with previous queries and user inputs.
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
