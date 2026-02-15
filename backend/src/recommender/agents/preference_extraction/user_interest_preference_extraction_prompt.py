from langchain_core.prompts import ChatPromptTemplate

# TODO improve prompt
user_interest_preference_extraction_prompt_template = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You extract user category preferences from raw user query.

        Rules:
        - Only fill categories stated or implied by the user.
        - Attach categories not only on exact match but also on semtic meaning.
        - Extract all categories mentioned, even if only implied.
        - If explicitly disliked, set strength=0 (do not omit it) and extracted_text must still be provided.
        - If not mentioned, keep it null.
        - Do not infer logistical preferences like budget, time of year, popularity, etc. --- IGNORE ---
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
