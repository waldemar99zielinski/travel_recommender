<h1 align="center">Hybrid User Interface with Agentic AI for Travel Destination Recommendation Application</h1>

<h3 align="center">Waldemar Zielinski</h3>

## Thesis Conspect Outline

### 1. Introduction

1. Motivation
2. Problem Statement
3. Research Objectives
    1. Investigate techniques for extracting user intents and travel preferences from unstructured natural language queries and mapping them to structured travel data to generate data-grounded recommendations.
    2. Examine how a hybrid user interface can bridge agentic AI reasoning and user interaction by presenting intermediate decision-making processes and recommendation outcomes in an interpretable format.
    3. Investigate mechanisms for maintaining contextual awareness across multi-turn conversations, enabling the continuous refinement of travel recommendations through natural language interactions.
    4. Design and develop a prototype travel destination recommendation system based on a hybrid user interface and agentic AI, incorporating intent extraction and data-grounded recommendations.
4. Thesis Structure

### 2. Background

1. Recommendation Systems
2. Large Language Models
3. Agentic AI
4. Hybrid Interfaces

### 3. Related Work
Base systems with classical interface approach:
- Destination finder https://destination-finder.netlify.app/
- DestiRec Cem Nasit Sarica, Investigating User Control to Influence Complex Recommender Systems

Agentic apporaches for travel recommendations:
   - Chen, T. (n.d.). Agentic AI for Trip Planning Optimization Application. arXiv. https://doi.org/10.48550/arXiv.2605.00276

   - Tandon, A., & Banerjee, A. (2025). Evaluating User Intent Classification and Hybrid Retrieval in a RAG-based Conversational Tourism Recommender System. CEUR Workshop Proceedings, 4052. https://ceur-ws.org/Vol-4052/paper5.pdf

   - Banerjee, A., Satish, A., Aisyah, F. N., Wörndl, W., & Deldjoo, Y. (2025). Collab-REC: An LLM-based Agentic Framework for Balancing Recommendations in Tourism. arXiv. https://doi.org/10.48550/arxiv.2508.15030

### 4. System Architecture
1. Overview
2. Backend
   1. Technologies Overview
   2. Data
      1. base dataset and its limitations
      2. requirements for dataset extension to better fit natural language queries
      3. interaction with the storage layer, agentic tools exposure
   3. Embeddings and LLM interactions
   4. Recommender
      1. Design Objectives
      2. Baseline Recommendation Approaches (for comparison)
         1. Single-Agent Recommendation with Full Prompt Context
         2. Single-Agent Recommendation with Tool-Based Retrieval from the SQL Database and Few-Shot Prompting, without Structured Workflow
      3. Multi-Agent Recommendation Framework
         1. Context-Aware Interpretation of User Requests
         2. User Preference Extraction and Constraint Derivation
            - regional preferences
            - seasonal preferences
            - budget-related preferences
         3. Aggregation of Travel Constraints into a Unified Recommendation Context
         4. Hybrid Retrieval and Candidate Recommendation Generation
            - embeddings-based semantic retrieval
            - direct keyword and text-based retrieval
            - application of extracted filters and results ranking
         5. Recommendation Enrichment and Response Construction
         6. Conversational Memory Persistence and Recommendation Refinement
   5. Exposed API
      1. user session
      2. travel destinations
      3. recommendation

3. Frontend

   1. Technologies Overview
   2. User Interface Design 
   3. Conversational Interaction Layer
   4. Graphical Interaction Layer
   5. Recommendation Presentations

4. Communication between components
   1. HTTP Request-Response Communication
   2. Limitations of Basic Request-Response Interaction 
      - in context of recommendation retrieval
   3. Server-Sent Events for Incremental Feedback

### 5. Evaluation
1. Synthetic Evaluation
focused soleley on the Recommendation Flow
   1. Synthetic Ground-Truth Dataset Construction
      - LLM-based construction of a golden dataset representing realistic travel recommendation scenarios
      - generation of personas with hard constraints and soft travel preferences
      - inclusion of single-turn and multi-turn conversational cases
      - simulation of evolving user preferences across multiple dialogue turns
   2. Evaluation Framework: Recommendation Relevance
      - comparison of naive recommendation approaches and the multi-agent recommendation framework on identical dialogue scenarios
      - assessment of constraint satisfaction and preference alignment in the returned recommendations
      - comparative relevance evaluation of final recommendation outputs
   3. Evaluation Framework: Context Persistence and Memory
      - testing whether earlier user constraints remain influential in later recommendation turns
      - assessment of contradiction rates across multi-turn conversations
      - evaluation of the system's ability to preserve and apply conversational state throughout the dialogue

2. User Survey-Based Evaluation 
based only on the Multi-Agent Recommendation Framework
focused on the user experience and application usability

```
1 (strongly disagree) to 5 (strongly agree) scoring

Q1. (Interface Adequacy)

I found the application interface intuitive to use.

Q2. (Conversational Interaction Quality)

The system accurately understood my travel requests and preferences.

Q3. (Conversational Flow)

The conversation with the system felt natural and logically connected.

Q4. (Conversational Consistency)

The system did not lose or misinterpret information that I provided during the conversation.

Q5. (Recommendation Relevance)

The recommended destinations matched my interests and travel needs.

Q6. (Recommendation Usefulness)

The recommendations helped me identify destinations I would consider visiting.

Q7. (Recommendation Transparency)

The region descriptions helped me understand how the recommended regions matched my travel preferences.

Q8. (System Responsiveness)

The system provided adequate feedback while processing my requests, and the waiting times were acceptable.

Q9. (Hybrid Interface Satisfaction)

The combination of conversational interaction and map-based visualization and regions descriptions enhanced my experience.

Q10. (Overall Satisfaction)

Overall, I am satisfied with the travel destination recommendation application.
```
### 6. Conclusion
