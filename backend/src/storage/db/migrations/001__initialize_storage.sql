CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS storage_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO storage_metadata (key, value)
VALUES ('embedding_dimension', '{{embedding_dimension}}')
ON CONFLICT (key) DO UPDATE
SET value = EXCLUDED.value,
    updated_at = CURRENT_TIMESTAMP;

CREATE OR REPLACE FUNCTION set_updated_at_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
