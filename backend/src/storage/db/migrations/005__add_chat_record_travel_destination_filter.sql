ALTER TABLE chat_record
ADD COLUMN IF NOT EXISTS travel_destination_filter JSONB NOT NULL DEFAULT '{}'::jsonb;
