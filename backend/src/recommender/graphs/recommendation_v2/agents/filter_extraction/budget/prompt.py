from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You update only the budget filters for the current recommendation_v2 chat turn.

            Inputs:
            - previous_budget_filter: the previously extracted budget filter from the last run
            - current_user_request: the raw user request for this turn

            previous_budget_filter format:
            - previous_budget_filter contains only one top-level field: `cost_term`.
            - `cost_term` may be null or omitted if there was no prior budget filter.
            - If present, `cost_term` must contain exactly one of these:
              - `explicit`
              - `inferred_level`
            - Never expect both at the same time.

            Expected values inside previous_budget_filter:
            - `cost_term.explicit.value`: the exact numeric amount previously extracted from the user request
            - `cost_term.explicit.operator`: max, min, or around
            - `cost_term.explicit.duration`: day, week, or month
            - `cost_term.inferred_level`: low, medium, or high

            Important semantics for explicit values:
            - `explicit` is for concrete money amounts the user gave.
            - Example: "I want to spend 200 euro per day" -> `explicit = { value: 200, operator: around, duration: day }`
            - Example: "I want to spend at most 150 euro per day" -> `explicit = { value: 150, operator: max, duration: day }`
            - Example: "I want to spend at least 300 per week" -> `explicit = { value: 300, operator: min, duration: week }`
            - Example: "I want to spend 700 for the trip" -> resolve that to `explicit = { value: 700, operator: around, duration: week }`
            - Assume an unspecified full trip lasts one week.
            - Do not convert explicit money amounts into low, medium, or high.

            previous_budget_filter examples:
            - {{"cost_term": null}}
            - {{"cost_term": {{"inferred_level": "low"}}}}
            - {{"cost_term": {{"explicit": {{"value": 700, "operator": "around", "duration": "week"}}}}}}

            Goal:
            - Return the updated budget filters after applying the current_user_request.
            - Treat current_user_request as an update to the previous budget filter.

            Rules:
            - Use only the `cost_term` field.
            - Keep previous budget filters if the user does not change them.
            - Remove budget filters if the user explicitly drops them, such as "any budget".
            - The output cost_term may contain either `explicit` or `inferred_level`, but never both.
            - Use `explicit` when the user directly gives a concrete money amount or bound that should be encoded structurally.
            - The explicit form must use:
              - value: the exact numeric amount the user gave
              - operator: max, min, or around
              - duration: day, week, or month
            - If the user gives a full-trip amount, resolve it to duration=week because the system assumes a trip lasts one week.
            - Use `inferred_level` only when the user implies a qualitative budget level but does not state an explicit money amount.
            - If `explicit` is present, omit `inferred_level`.
            - If `inferred_level` is present, omit `explicit`.
            - Do not return region, season, or month filters.
            - Return only the `cost_term` field.

            Examples:
            - "cheap trip" -> cost_term.inferred_level = low
            - "luxury escape" -> cost_term.inferred_level = high
            - "I want to spend 200 euro per day" -> cost_term.explicit = {{ value: 200, operator: around, duration: day }}
            - "I want to spend at most 150 euro per day" -> cost_term.explicit = {{ value: 150, operator: max, duration: day }}
            - "I want to spend at least 300 per week" -> cost_term.explicit = {{ value: 300, operator: min, duration: week }}
            - "I want to spend 700 for the trip" -> cost_term.explicit = {{ value: 700, operator: around, duration: week }}
            """,
        ),
        (
            "user",
            """
            previous_budget_filter:
            {previous_budget_filter}

            current_user_request:
            {current_user_request}
            """,
        ),
    ]
)
