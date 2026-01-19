from langchain_core.prompts import ChatPromptTemplate

prompt_tempalate = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You extract user category preferences from raw user query.

        Rules:
        - Only fill categories stated or implied by the user.
        - Attach categories not only on exact match but also on semtic meaning.
        - Extract all categories mentioned, even if only implied.
        - If explicitly disliked, set strength=0 (do not omit it).
        - If not mentioned, keep it null.
        - extracted_text must be a short snippet from the user messages supporting the preference.
        - strength must be integer 0..5.
        """
    ),
    (
        "user",
        """
        Raw initial user query:
        {raw_user_query}
        """,
    )
])