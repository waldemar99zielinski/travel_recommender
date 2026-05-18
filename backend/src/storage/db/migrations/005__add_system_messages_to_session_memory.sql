ALTER TABLE recommendation_session_memory
ADD COLUMN IF NOT EXISTS system_messages JSONB NOT NULL DEFAULT '[]'::jsonb;
