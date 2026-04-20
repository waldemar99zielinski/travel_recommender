CREATE TABLE IF NOT EXISTS recommendation_session_memory (
    user_id UUID NOT NULL DEFAULT uuidv7(),
    session_id UUID NOT NULL DEFAULT uuidv7(),
    chat_history_number INTEGER NOT NULL,
    user_request TEXT NOT NULL DEFAULT '',
    system_response TEXT NOT NULL DEFAULT '',
    query TEXT NOT NULL DEFAULT '',
    interest_preference JSONB NOT NULL DEFAULT '{}'::jsonb,
    logistical_preference JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, session_id, chat_history_number)
);

CREATE TRIGGER trg_recommendation_session_memory_updated_at
BEFORE UPDATE ON recommendation_session_memory
FOR EACH ROW
EXECUTE FUNCTION set_updated_at_timestamp();
