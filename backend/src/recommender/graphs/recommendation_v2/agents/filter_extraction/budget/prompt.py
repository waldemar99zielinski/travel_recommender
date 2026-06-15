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
            - Example: "I want to spend 200 euro per day" -> `explicit = {{"value": 200, "operator": "around", "duration": "day"}}`
            - Example: "I want to spend at most 150 euro per day" -> `explicit = {{"value": 150, "operator": "max", "duration": "day"}}`
            - Example: "I want to spend at least 300 per week" -> `explicit = {{"value": 300, "operator": "min", "duration": "week"}}`
            - Example: "I want to spend 700 for the trip" -> resolve that to `explicit = {{"value": 700, "operator": "around", "duration": "week"}}`
            - Assume an unspecified full trip lasts one week.
            - Do not convert explicit money amounts into low, medium, or high.

            previous_budget_filter examples:
            - {{"cost_term": null}}
            - {{"cost_term": {{"inferred_level": "low"}}}}
            - {{"cost_term": {{"explicit": {{"value": 700, "operator": "around", "duration": "week"}}}}}}

            Goal:
            - Return the updated budget filters after applying the current_user_request.
            - Treat current_user_request as an update to the previous budget filter.
            - Always return both fields: `filter_removed` and `cost_term`.

            Rules:
            - Use only the `filter_removed` and `cost_term` fields.
            - Set filter_removed=true only when current_user_request explicitly says to remove, clear, drop, reset, ignore, or stop using all filters/constraints, or explicitly says to remove, clear, drop, reset, ignore, or stop using the budget, price, cost, spending, cheap, affordability, or luxury filter specifically.
            - Do not set filter_removed=true for vague preference changes, such as "something different", "more flexible", "less strict", "show more options", or "not that important", unless the user explicitly mentions removing all filters or removing the budget-related filter.
            - If current_user_request explicitly removes all filters/constraints, output exactly: {{"filter_removed": true, "cost_term": null}}.
            - If current_user_request explicitly removes the budget-related filter, output exactly: {{"filter_removed": true, "cost_term": null}}.
            - Do not keep a previous cost_term after an explicit budget or all-filter removal request.
            - If no budget filter is explicitly removed, set filter_removed=false.
            - Add or update `cost_term` if and only if the user mentions budget, price, cost, spending, affordability, cheapness, luxury, or another clear money-related context.
            - Keep previous budget filters if the user does not change them.
            - Remove budget filters if the user explicitly drops, clears, or removes them, such as "any budget", "remove the budget filter", "drop the cheap filter", or "budget does not matter anymore".
            - The output cost_term may contain either `explicit` or `inferred_level`, but never both.
            - Use `explicit` when the user directly gives a concrete money amount or bound that should be encoded structurally.
            - The explicit form must use:
              - value: the exact numeric amount the user gave
              - operator: max, min, or around
              - duration: day, week, or month
            - If the user gives a full-trip amount, resolve it to duration=week because the system assumes a trip lasts one week.
            - Use `inferred_level` only when the user implies a qualitative budget level but does not state an explicit money amount.
            - Do not infer a budget filter from standalone adjectives with no money context.
            - Words like "low", "high", or "extreme" by themselves are not budget signals unless they clearly refer to price, budget, cost, or spending.
            - If `explicit` is present, omit `inferred_level`.
            - If `inferred_level` is present, omit `explicit`.
            - Do not return region, season, or month filters.
            - Return only the `filter_removed` and `cost_term` fields.

            Examples:
            - "I want a cheap beach trip in southern Europe this summer" -> cost_term.inferred_level = low
            - "Plan a luxury escape with great hotels and fine dining" -> cost_term.inferred_level = high
            - "I want a destination with a low-key vibe and quiet beaches" -> no cost_term
            - "Show me places with high mountains and scenic hiking" -> no cost_term
            - "I want an extreme adventure with surfing and nightlife" -> no cost_term
            - "Find me a high-energy city with clubs and live music" -> no cost_term
            - "I want a low budget trip with good food and warm weather" -> cost_term.inferred_level = low
            - "I want to spend around 200 euro per day for a sunny island holiday" -> cost_term.explicit = {{"value": 200, "operator": "around", "duration": "day"}}
            - "For this city break, I want to spend at most 150 euro per day" -> cost_term.explicit = {{"value": 150, "operator": "max", "duration": "day"}}
            - "I am okay spending at least 300 per week if the beaches are excellent" -> cost_term.explicit = {{"value": 300, "operator": "min", "duration": "week"}}
            - "I want to spend about 700 for the whole trip and prefer somewhere warm" -> cost_term.explicit = {{"value": 700, "operator": "around", "duration": "week"}}
            - previous_budget_filter: {{"cost_term": {{"inferred_level": "low"}}}}
              current_user_request: "Actually, any budget is fine now"
              output: {{"filter_removed": true, "cost_term": null}}
            - previous_budget_filter: {{"cost_term": {{"explicit": {{"value": 200, "operator": "max", "duration": "day"}}}}}}
              current_user_request: "Remove the budget filter"
              output: {{"filter_removed": true, "cost_term": null}}
            - previous_budget_filter: {{"cost_term": {{"inferred_level": "low"}}}}
              current_user_request: "Drop the cheap filter"
              output: {{"filter_removed": true, "cost_term": null}}
            - previous_budget_filter: {{"cost_term": {{"inferred_level": "low"}}}}
              current_user_request: "remove all constraints"
              output: {{"filter_removed": true, "cost_term": null}}
            - previous_budget_filter: {{"cost_term": {{"explicit": {{"value": 300, "operator": "max", "duration": "week"}}}}}}
              current_user_request: "clear every filter and show me anything"
              output: {{"filter_removed": true, "cost_term": null}}
            - previous_budget_filter: {{"cost_term": {{"inferred_level": "high"}}}}
              current_user_request: "reset all constraints"
              output: {{"filter_removed": true, "cost_term": null}}
            - previous_budget_filter: {{"cost_term": {{"inferred_level": "low"}}}}
              current_user_request: "show me more flexible options"
              output: {{"filter_removed": false, "cost_term": {{"inferred_level": "low"}}}}
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
