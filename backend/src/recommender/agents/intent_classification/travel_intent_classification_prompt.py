from langchain_core.prompts import ChatPromptTemplate


travel_intent_classification_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You classify the intent of an in-scope travel message.

            Use intent=recommendation when the user wants destination suggestions or wants to refine
            the search by changing budget, timing, activities, region, or similar constraints.

            Use intent=conversation when the user is asking a travel follow-up question that should be
            answered conversationally, such as asking for explanation, comparison, pros and cons, or
            clarifying what a suggested destination is like.

            If the message asks for cheaper, quieter, warmer, more cultural, or otherwise different
            alternatives, classify it as recommendation because the retrieval set should change.

            Return a short reason.
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
