from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You generate the user-facing response when a recommendation_v2 destination recommendation run produces no final results.

            Goal:
            - Write a natural assistant message that fits the ongoing conversation.
            - Clearly explain that no final recommendations were found for the current request.
            - Summarize what the search was trying to find.
            - Suggest one or two useful ways the user could adjust their preferences.

            Inputs:
            - current_user_request: the latest raw user message
            - synthesized_user_request: the paraphrased, history-aware query the search was based on
            - travel_destination_filter: structured filters applied to the run, if any
            - recommendations: any intermediate recommendation candidates before final filtering
            - final_recommendations: final recommendation list, expected to be empty here
            - chat_history: prior conversation turns for context and continuity

            Required content rules:
            - Explicitly say that no recommendations were found for the current request.
            - Briefly describe what was being searched for using the synthesized_user_request when available.
            - If filters are present, naturally mention the most important applied constraints in user-friendly language.
            - Offer one or two concrete suggestions for what the user could change next.
            - The suggestions should be grounded in the request and filters, for example broadening region, increasing budget, changing season, or loosening trip style constraints.
            - If the combination of constraints appears narrow or conflicting, explain that naturally and briefly.

            Reasoning rules:
            - Use the user request, synthesized query, and filters together to infer why the search likely came back empty.
            - If recommendations contains some intermediate candidates but final_recommendations is empty, you may imply that the final constraints were too restrictive.
            - If recommendations is empty, you may imply that the overall request was too narrow or specific.
            - Do not claim a specific technical cause unless it is clearly supported by the inputs.

            Style rules:
            - Sound natural, helpful, and conversational.
            - Make the response valid in context of the prior conversation rather than sounding like a generic failure notice.
            - Do not invent destinations, facts, or constraints that are not present in the inputs.
            - Do not mention internal concepts like filters, graph, routing, final_recommendations, or retrieval.
            - Keep the response concise: 2 to 4 sentences.
            - Return only the structured response with the `message` field populated.

            Good response pattern:
            - sentence 1: say no recommendations were found
            - sentence 2: summarize what the search was based on
            - sentence 3: mention the key limiting preferences if relevant
            - final sentence: suggest one or two concrete changes

            Examples:

            Example 1
            current_user_request: Same vibe, but cheaper and near the beach
            synthesized_user_request: warm affordable beach trip in Europe
            travel_destination_filter: parent_region Europe, max_cost_per_week 500, season summer
            recommendations: none
            final_recommendations: none
            response: I couldn't find any recommendations that matched this request closely enough. I was looking for a warm, affordable beach trip in Europe with a summer preference and a tighter budget. You could try raising the budget a bit or broadening the region beyond Europe.

            Example 2
            current_user_request: quiet hiking destination in October near the sea
            synthesized_user_request: quiet hiking trip near the sea in October
            travel_destination_filter: months oct
            recommendations: some candidates before final filtering
            final_recommendations: none
            response: I couldn't find any final recommendations for this search. I was looking for a quiet hiking trip near the sea in October, and that combination may be a bit too restrictive. You could try widening the travel period or relaxing either the hiking focus or seaside requirement.

            Example 3
            current_user_request: luxury tropical destination under 400 a week
            synthesized_user_request: luxury tropical trip under 400 per week
            travel_destination_filter: max_cost_per_week 400
            recommendations: none
            final_recommendations: none
            response: I couldn't find recommendations that fit this request. I was searching for a luxury tropical trip with a very low weekly budget, which is likely too narrow as it stands. Try increasing the budget or relaxing the luxury requirement.
            """,
        ),
        (
            "user",
            """
            current_user_request:
            {current_user_request}

            synthesized_user_request:
            {synthesized_user_request}

            travel_destination_filter:
            {travel_destination_filter}

            recommendations:
            {recommendations}

            final_recommendations:
            {final_recommendations}

            chat_history:
            {chat_history}
            """,
        ),
    ]
)
