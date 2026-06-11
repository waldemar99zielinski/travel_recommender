from langchain_core.prompts import ChatPromptTemplate


travel_scope_classification_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You classify whether the assistant should handle the current message.

            The assistant handles only travel recommendation work:
            - destination recommendations
            - refining recommendation constraints
            - follow-up questions about travel options already being discussed
            - comparison or explanation of destinations in the current travel context

            Mark the message as in_scope when it is a short follow-up that depends on an existing
            travel conversation, even if the raw message alone is underspecified.

            Mark the message as out_of_scope when it asks for help unrelated to travel planning or
            travel recommendations, such as coding, math, unrelated factual questions, or general chat.

            Return a short reason that explains the decision.
            """,
        ),
        (
            "user",
            """
            Current user input:
            {current_user_input}

            Synthesized travel-aware query:
            {synthesized_query}
            """,
        ),
    ]
)
