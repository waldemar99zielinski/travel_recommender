CREATE TABLE IF NOT EXISTS travel_destinations (
    id TEXT PRIMARY KEY,
    parent_region TEXT NOT NULL,
    region TEXT NOT NULL,
    popularity DOUBLE PRECISION NOT NULL,
    cost_per_week DOUBLE PRECISION NOT NULL,
    jan DOUBLE PRECISION NOT NULL,
    feb DOUBLE PRECISION NOT NULL,
    mar DOUBLE PRECISION NOT NULL,
    apr DOUBLE PRECISION NOT NULL,
    may DOUBLE PRECISION NOT NULL,
    jun DOUBLE PRECISION NOT NULL,
    jul DOUBLE PRECISION NOT NULL,
    aug DOUBLE PRECISION NOT NULL,
    sep DOUBLE PRECISION NOT NULL,
    oct DOUBLE PRECISION NOT NULL,
    nov DOUBLE PRECISION NOT NULL,
    dec DOUBLE PRECISION NOT NULL,
    nature DOUBLE PRECISION NOT NULL,
    hiking DOUBLE PRECISION NOT NULL,
    beach DOUBLE PRECISION NOT NULL,
    watersports DOUBLE PRECISION NOT NULL,
    entertainment DOUBLE PRECISION NOT NULL,
    wintersports DOUBLE PRECISION NOT NULL,
    culture DOUBLE PRECISION NOT NULL,
    culinary DOUBLE PRECISION NOT NULL,
    architecture DOUBLE PRECISION NOT NULL,
    shopping DOUBLE PRECISION NOT NULL,
    description TEXT NOT NULL,
    embedding vector({{embedding_dimension}}) NOT NULL,
    embedding_version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

DROP TRIGGER IF EXISTS trg_travel_destinations_updated_at ON travel_destinations;

CREATE TRIGGER trg_travel_destinations_updated_at
BEFORE UPDATE ON travel_destinations
FOR EACH ROW
EXECUTE FUNCTION set_updated_at_timestamp();

CREATE INDEX IF NOT EXISTS ix_travel_destinations_parent_region
ON travel_destinations (parent_region);

CREATE INDEX IF NOT EXISTS ix_travel_destinations_embedding_hnsw
ON travel_destinations USING hnsw (embedding vector_l2_ops);
