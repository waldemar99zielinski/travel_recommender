from __future__ import annotations

from region_description_generation.paths import ensure_src_path

ensure_src_path()

from storage.configuration import load_storage_configuration
from storage.db.engine import create_storage_engine
from storage.db.session import create_session_factory
from storage.db.unit_of_work import StorageUnitOfWork
from storage.models.travel_destination import TravelDestinationRecord
from storage.stores.travel_destination_store import TravelDestinationStore


class ReadOnlyEmbeddingModel:
    """Minimal embedding-model stub used for store operations that do not embed queries."""

    def get_dimentions(self) -> int:
        """Return a positive placeholder dimension required by TravelDestinationStore."""
        return 1

    def embed_query(self, query: str) -> list[float]:
        """Reject embedding calls because this script only reads stored destinations."""
        raise NotImplementedError("This script only uses read-only TravelDestinationStore methods.")


def load_regions_from_store() -> list[TravelDestinationRecord]:
    """Load persisted travel destinations using the existing TravelDestinationStore facade."""
    configuration = load_storage_configuration()
    engine = create_storage_engine(configuration.engine)
    session_factory = create_session_factory(engine)
    unit_of_work = StorageUnitOfWork(session_factory=session_factory)
    store = TravelDestinationStore(
        unit_of_work,
        embedding_model=ReadOnlyEmbeddingModel(),
    )

    try:
        return sorted(store.all(), key=lambda record: record.id)
    finally:
        engine.dispose()


def select_target_records(
    records: list[TravelDestinationRecord],
    *,
    region_ids: list[str],
    limit: int | None,
) -> list[TravelDestinationRecord]:
    """Select which persisted destinations should be regenerated."""
    selected = records
    if region_ids:
        requested_ids = {region_id.strip() for region_id in region_ids if region_id.strip()}
        selected = [record for record in records if record.id in requested_ids]

        missing_ids = sorted(requested_ids - {record.id for record in selected})
        if missing_ids:
            raise ValueError(f"Unknown region id(s): {', '.join(missing_ids)}")

    if limit is not None:
        selected = selected[:limit]

    return selected
