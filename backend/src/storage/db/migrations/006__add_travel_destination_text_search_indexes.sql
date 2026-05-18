CREATE INDEX IF NOT EXISTS ix_travel_destinations_region_lower
ON travel_destinations ((lower(region)));

CREATE INDEX IF NOT EXISTS ix_travel_destinations_parent_region_lower
ON travel_destinations ((lower(parent_region)));

CREATE INDEX IF NOT EXISTS ix_travel_destinations_search_document_gin
ON travel_destinations
USING gin (
    to_tsvector(
        'simple',
        coalesce(region, '') || ' ' || coalesce(parent_region, '') || ' ' || coalesce(description, '')
    )
);
