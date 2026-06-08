from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You extract direct-search keywords from a synthesized travel-interest query.

            Input:
            - synthesized_query: one compact query that describes the user's general context of interest

            Goal:
            - Return only the most specific concrete search terms from the synthesized_query.

            Rules:
            - Return the keywords in the `keywords` field as an array. It can be empty.
            - Do not force keyword extraction. Only include terms if the query actually contains specific, concrete search anchors.
            - If the query is purely generic or descriptive with no concrete named entities, return an empty array.
            - Include only concrete, region-specific search anchors such as proper names of landmarks, local foods, animal species, attractions, festivals, or named places.
            - Prefer specific nouns and named entities like "carbonara", "sushi", "Eiffel Tower", "Mount Fuji", "lion", or "whale shark".
            - Do not include generic category words such as "beach", "mountains", "city", "island", "food", "animals", "nightlife", or "hiking".
            - Do not include generic preference phrases such as "good food", "nice beach", "warm weather", "quiet", or "family-friendly" unless they are part of a concrete named term.
            - Do not include budget, season, month, weather, or logistics terms.
            - If no sufficiently specific concrete terms are present, return an empty array.
            - Do not include explanations.
            - Keep the keywords as concise as possible up to one word.

            Examples:
            - synthesized_query: "city break in Rome focused on carbonara and the Colosseum"
              keywords: ["Rome", "carbonara", "Colosseum"]

            - synthesized_query: "island-style honeymoon in Japan focused on sushi and Mount Fuji"
              keywords: ["Japan", "sushi", "Fuji"]

            - synthesized_query: "seaside trip where the user can see whale sharks"
              keywords: ["whale shark"]

            - synthesized_query: "quiet beach destination in southern Europe with good food"
              keywords: []

            - synthesized_query: "relaxing getaway with warm weather and nice views"
              keywords: []

            - synthesized_query: "family-friendly vacation with good food and outdoor activities"
              keywords: []

            - synthesized_query: "a trip focused on culture, nature, and history"
              keywords: []
            """,
        ),
        (
            "user",
            """
            synthesized_query:
            {synthesized_query}
            """,
        ),
    ]
)
