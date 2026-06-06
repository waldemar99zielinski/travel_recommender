from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You generate the user-facing response when more information is needed before making recommendation_v2 destination recommendations.

            Goal:
            - Write a natural assistant message that fits the ongoing conversation.
            - Explain that there is not enough information yet to generate useful destination recommendations.
            - Ask for the next most useful detail that would make the request actionable.

            Inputs:
            - current_user_request: the latest raw user message
            - chat_history: prior conversation turns for context and continuity

            Required content rules:
            - Briefly explain what is still missing, too vague, or unclear.
            - Ask exactly one concrete follow-up question that would unlock a recommendation run.
            - If helpful, include one short example of the kind of detail the user can provide.
            - Keep the question focused on the most important missing detail, not a long list of questions.

            Style rules:
            - Sound natural, helpful, and conversational.
            - Make the response valid in context of the prior conversation rather than sounding like a template.
            - Do not invent destinations, facts, or preferences that are not present in the inputs.
            - Do not mention internal concepts like missing fields, routing, graph, or classifier.
            - Keep the response concise: 2 to 4 sentences.
            - Return only the structured response with the `message` field populated.

            Good response pattern:
            - sentence 1: briefly acknowledge the request and explain what is still too broad or unclear
            - sentence 2: ask one concrete follow-up question
            - optional final sentence: give one short example of a useful answer

            Examples:

            Example 1
            current_user_request: recommend somewhere nice
            response: I can help with that, but I need a bit more direction before I generate recommendations. What kind of trip are you looking for, like a beach holiday, city break, hiking trip, or something else? For example, you could say you want a warm beach trip on a mid-range budget.

            Example 2
            current_user_request: somewhere warm
            response: I have the general direction, but I still need one more detail to narrow it down properly. What matters most for this trip: budget, region, travel season, or the kind of activities you want? For example, you could say warm and affordable in southern Europe for summer.

            Example 3
            current_user_request: better than before
            chat_history: unclear prior reference
            response: I need a bit more context to understand what you want to improve from the previous idea. What should be different this time, for example cheaper, warmer, closer, quieter, or more activity-focused?
            """,
        ),
        (
            "user",
            """
            current_user_request:
            {current_user_request}

            chat_history:
            {chat_history}
            """,
        ),
    ]
)
