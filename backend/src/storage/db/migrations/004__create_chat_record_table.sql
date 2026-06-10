CREATE TABLE IF NOT EXISTS chat_record (
    user_id UUID NOT NULL DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL DEFAULT gen_random_uuid(),
    chat_history_number INTEGER NOT NULL,
    user_request TEXT NOT NULL DEFAULT '',
    system_response TEXT NOT NULL DEFAULT '',
    synthesized_query TEXT NOT NULL DEFAULT '',
    included_regions_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    excluded_regions_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    recommendations JSONB NOT NULL DEFAULT '[]'::jsonb,
    travel_destinations_evaluations JSONB NOT NULL DEFAULT '[]'::jsonb,
    graph_version VARCHAR NOT NULL DEFAULT '',
    message_type VARCHAR NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, session_id, chat_history_number)
);
