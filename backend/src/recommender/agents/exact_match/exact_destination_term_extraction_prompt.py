from langchain_core.prompts import ChatPromptTemplate


exact_destination_term_extraction_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You extract explicit travel place terms that should trigger exact destination lookup.

            Include only terms that directly name a specific place or landmark, such as:
            - countries
            - regions
            - cities
            - landmarks
            - famous subregions strongly tied to a destination

            Good examples:
            - Vatican
            - Mount Everest
            - Amalfi Coast
            - Nepal
            - Ibiza

            Rules:
            - Return at most 3 candidates.
            - Keep each phrase short and search-friendly.
            - Prefer exact surface forms from the user query or synthesized query.
            - Do not invent places.
            - If no explicit place term is present, return an empty candidates list.
            - Confidence must be a float from 0.0 to 1.0.
            """,
        ),
        (
            "user",
            """
            Current user input:
            {current_user_input}

            Synthesized query:
            {synthesized_query}
            """,
        ),
    ]
)
