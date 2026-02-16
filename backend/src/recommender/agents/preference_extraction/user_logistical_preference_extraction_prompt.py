from langchain_core.prompts import ChatPromptTemplate

user_logistical_preference_extraction_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You extract user logistical travel preferences from a raw user query.

            Extract only these sections:
            - price
            - popularity
            - time_of_year

            Rules:
            - Keep each section null if not present in user input explicitly or implicitly.
            - For price, capture user intent for min, max, budget tier.
            - For popularity, capture whether the user prefers to avoid crowded places (rank 0) or wants more popular and crowded places (rank 5)
                - ranks are integers in range 0..5, where:
                - 0 = user does not like crowds and prefers less known location
                - 5 = user prefers popular places and does not mind crowds.
            - For time_of_year, capture months and/or season if present.
            - extracted_text must be a short snippet from the user query that supports the extracted preference.
            """,
        ),
        (
            "user",
            """
            Raw initial user query:
            {raw_user_query}
            """,
        ),
    ]
)
