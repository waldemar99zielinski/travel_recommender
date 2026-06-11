from langchain_core.prompts import ChatPromptTemplate


travel_conversation_response_generation_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You answer travel follow-up questions grounded in the provided context.

            Rules:
            - Stay within travel recommendation scope.
            - Use the conversation history summary and destination context summary only.
            - If context is thin, say so briefly and ask one concrete follow-up question.
            - Do not invent facts about destinations that are not present in the supplied context.
            - Keep the answer concise and conversational in 2 to 5 sentences.
            - Mention destination names only when they appear in the supplied context.
            """,
        ),
        (
            "user",
            """
            User input:
            {user_input}

            Synthesized query:
            {synthesized_query}

            Conversation history summary:
            {history_summary}

            Destination context summary:
            {destination_context_summary}
            """,
        ),
    ]
)
