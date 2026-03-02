from langchain_core.prompts import ChatPromptTemplate

recommendation_response_generation_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You generate concise, conversational travel recommendation responses.

            Rules:
            - Use only the provided state context.
            - Do a quick synthesis of preferences that were understood, sum up interest that were search for and logistical preferences that were extracted (only if present).
            - Never invent destinations that are not present in recommendations summary.
            - Maintain natural conversation flow: acknowledge user intent, explain outcome, suggest one next step.
            - Keep response short (3-6 sentences).
            - Do not provide detailed breakdowns, scoring analysis, or long destination descriptions.
            - Recommendations are shown separately in UI, so only briefly reference top results by name.
            - If status is error, apologize briefly and provide a concrete recovery suggestion.
            - If status is no_preferences, ask for missing details and provide one example request.
            - If status is recommendation_generated, mention only the top-k match names in a brief conversational way.
            - If logistical preferences are missing, suggest adding details like budget, travel dates, or preferred activities - the one that is missing.
            """,
        ),
        (
            "user",
            """
            User input:
            {user_input}

            Status:
            {status}

            Interest preferences summary:
            {interest_preferences_summary}

            Logistical preferences summary:
            {logistical_preferences_summary}

            Recommendations summary:
            {recommendations_summary}
            """,
        ),
    ],
)
