from __future__ import annotations

from langchain_core.documents import Document

from recommender.models.data_flow.recommendation_output import Recommendation
from recommender.models.data_flow.travel_destination import TravelDestination


class TravelDestinationDocumentMapper:
    """Maps travel destination models to/from FAISS documents."""

    def to_document(self, destination: TravelDestination, source: str) -> Document:
        content = (
            f"Destination: {destination.region}, located in {destination.parent_region}. "
            f"Overview: {destination.description}"
        )

        metadata = {
            "source": source,
            **destination.model_dump(),
        }
        return Document(page_content=content, metadata=metadata)

    def to_recommendation(self, doc: Document, embedding_score: float, source: str) -> Recommendation:
        metadata = doc.metadata
        return Recommendation(
            embedding_score=float(embedding_score),
            ranking_score=None,
            content=doc.page_content,
            source=str(metadata.get("source", source)),
            parent_region=str(metadata["parent_region"]),
            region=str(metadata["region"]),
            u_name=str(metadata["u_name"]),
            popularity=float(metadata["popularity"]),
            cost_per_week=float(metadata["cost_per_week"]),
            jan=float(metadata["jan"]),
            feb=float(metadata["feb"]),
            mar=float(metadata["mar"]),
            apr=float(metadata["apr"]),
            may=float(metadata["may"]),
            jun=float(metadata["jun"]),
            jul=float(metadata["jul"]),
            aug=float(metadata["aug"]),
            sep=float(metadata["sep"]),
            oct=float(metadata["oct"]),
            nov=float(metadata["nov"]),
            dec=float(metadata["dec"]),
            nature=float(metadata["nature"]),
            hiking=float(metadata["hiking"]),
            beach=float(metadata["beach"]),
            watersports=float(metadata["watersports"]),
            entertainment=float(metadata["entertainment"]),
            wintersports=float(metadata["wintersports"]),
            culture=float(metadata["culture"]),
            culinary=float(metadata["culinary"]),
            architecture=float(metadata["architecture"]),
            shopping=float(metadata["shopping"]),
            description=str(metadata["description"]),
        )
