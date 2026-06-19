CREATE TABLE IF NOT EXISTS survey_questions (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    question_text TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS survey_results (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id UUID NOT NULL,
    session_id UUID NOT NULL,
    results JSONB NOT NULL DEFAULT '{}'::jsonb,
    comment TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_survey_results_user_id
ON survey_results (user_id);

CREATE INDEX IF NOT EXISTS ix_survey_results_session_id
ON survey_results (session_id);
