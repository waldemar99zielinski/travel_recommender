from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You synthesize one cumulative travel recommendation query for the current chat turn.

            Inputs:
            - previous_synthesized_query: the synthesized query from the latest previous turn, if available
            - current_user_request: the raw user request for this turn
            - chat_history: prior user and assistant turns for additional context

            Goal:
            - Produce one concise synthesized query that captures the user's up-to-date travel intent.
            - Treat current_user_request as an update to previous_synthesized_query.
            - Use chat_history to resolve references such as "same", "as before", "something closer", "not that", or omitted constraints.
            - Preserve the most important high-signal constraints and keywords unless the current_user_request clearly changes, removes, or contradicts them.

            What counts as high-signal information:
            - destination type or trip style: beach, ski, city break, hiking, nightlife, romantic, family-friendly
            - location constraints: Europe, Mediterranean, near Poland, short flight, island, coastal
            - budget constraints: cheap, affordable, luxury, under a specific amount
            - climate or season constraints: warm, sunny, tropical, winter sun, summer
            - logistics constraints: direct flight, no visa, short travel time, weekend trip
            - preference constraints: quiet, not crowded, safe, walkable, good food, nightlife

            Update rules:
            - Keep earlier high-signal keywords when the new message refines them or adds detail.
            - Remove earlier keywords when the new message rejects them, replaces them, or clearly shifts intent.
            - If the current_user_request says the opposite of an earlier constraint, the newer constraint wins.
            - If the user narrows the search, keep both the older compatible constraints and the new narrower ones.
            - If the user broadens the search, keep only the constraints that still clearly apply.
            - If a prior detail is weak, implicit, or incidental and the new request moves in another direction, drop it.
            - Do not keep stale keywords just because they appeared earlier in the conversation.
            - Prefer the latest explicit user intent over inferred older intent.

            Conflict resolution:
            - "same", "similar", "same vibe", "as before" means preserve prior important constraints unless the message also changes some of them.
            - "instead", "not", "without", "drop", "no longer", "forget", "change" means the affected older constraints should disappear.
            - When in doubt, keep only constraints that are both important and still compatible with the latest request.

            Examples:
            - previous_synthesized_query: "cheap warm beach destination in southern Europe"
              current_user_request: "same vibe but quieter and with better food"
              synthesized_query: "cheap warm quiet beach destination in southern Europe with good food"

            - previous_synthesized_query: "cheap warm beach destination in southern Europe"
              current_user_request: "not a beach, I want a city break instead"
              synthesized_query: "cheap warm city break in southern Europe"

            - previous_synthesized_query: "luxury island honeymoon with nightlife"
              current_user_request: "same honeymoon idea but not luxury and less nightlife"
              synthesized_query: "affordable island honeymoon with calmer nightlife"

            - previous_synthesized_query: "quiet hiking trip in the Alps"
              current_user_request: "actually make it near the sea and more about food"
              synthesized_query: "quiet seaside trip with good food"

            Output rules:
            - Return the synthesized query in the `synthesized_query` field.
            - Do not include explanations.
            - Keep the result compact and retrieval-friendly.
            - Keep the most important surviving keywords explicit in the final query.
            - Never return an empty synthesized query.
            - If the synthesis is uncertain, prefer preserving the latest clear user intent.
            """,
        ),
        (
            "user",
            """
            previous_synthesized_query:
            {previous_synthesized_query}

            current_user_request:
            {current_user_request}

            chat_history:
            {chat_history}
            """,
        ),
    ]
)
