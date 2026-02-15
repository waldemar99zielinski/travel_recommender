from __future__ import annotations

import csv
from typing import Optional

from langchain_core.documents import Document

from recommender.models.data_flow.recommendation_output import RecommendationBase

class TravelDataParser:
    """
        Parse travel CSV rows into documents.
    """

    def parse_csv_to_documents(self, csv_filepath: str) -> list[Document]:
        """Read a travel CSV file and convert valid rows to documents."""
        documents: list[Document] = []

        with open(csv_filepath, mode="r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file, delimiter=";")
            for row in reader:
                document = self._parse_row(row=row, csv_filepath=csv_filepath)
                if document is not None:
                    documents.append(document)

        return documents

    def _parse_row(self, row: dict[str, str], csv_filepath: str) -> Optional[Document]:
        region = self._pick(row, "Region", "region")
        description = self._pick(row, "Description", "description")
        parent_region = self._pick(row, "Parent_region", "parent_region")

        if region is None or description is None:
            return None

        location = f"Destination: {region}"
        if parent_region is not None:
            location += f", located in {parent_region}"

        content = f"{location}. Overview: {description}"
        metadata = {
            "source": csv_filepath,
            "parent_region": parent_region or "World",
            "region": region,
            "u_name": self._pick(row, "u_name"),
            "popularity": self._pick(row, "popularity"),
            "cost_per_week": self._to_optional_float(self._pick(row, "costPerWeek", "cost_per_week")),
            "jan": self._pick(row, "jan"),
            "feb": self._pick(row, "feb"),
            "mar": self._pick(row, "mar"),
            "apr": self._pick(row, "apr"),
            "may": self._pick(row, "may"),
            "jun": self._pick(row, "jun"),
            "jul": self._pick(row, "jul"),
            "aug": self._pick(row, "aug"),
            "sep": self._pick(row, "sep"),
            "oct": self._pick(row, "oct"),
            "nov": self._pick(row, "nov"),
            "dec": self._pick(row, "dec"),
            "safety": self._pick(row, "safety"),
            "nature": self._pick(row, "nature"),
            "hiking": self._pick(row, "hiking"),
            "beach": self._pick(row, "beach"),
            "watersports": self._pick(row, "watersports"),
            "entertainment": self._pick(row, "entertainment"),
            "wintersports": self._pick(row, "wintersports"),
            "culture": self._pick(row, "culture"),
            "culinary": self._pick(row, "culinary"),
            "architecture": self._pick(row, "architecture"),
            "shopping": self._pick(row, "shopping"),
            "description": description,
        }

        return Document(page_content=content, metadata=metadata)

    def _pick(self, row: dict[str, str], *keys: str) -> Optional[str]:
        for key in keys:
            if key in row:
                value = self._normalize_value(row.get(key))
                if value is not None:
                    return value
        return None

    def _normalize_value(self, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip()
        return normalized if normalized else None

    def _to_optional_float(self, value: Optional[str]) -> Optional[float]:
        normalized = self._normalize_value(value)
        if normalized is None:
            return None
        try:
            return float(normalized)
        except ValueError:
            return None

    def convert_to_recommendation_output(self, doc: Document, score: float, source: str) -> RecommendationBase:
        return RecommendationBase(
            score=float(score),
            content=doc.page_content,
            source=str(doc.metadata.get("source", source)),
            parent_region=doc.metadata.get("parent_region"),
            region=doc.metadata.get("region"),
            u_name=doc.metadata.get("u_name"),
            popularity=doc.metadata.get("popularity"),
            cost_per_week=doc.metadata.get("cost_per_week"),
            jan=doc.metadata.get("jan"),
            feb=doc.metadata.get("feb"),
            mar=doc.metadata.get("mar"),
            apr=doc.metadata.get("apr"),
            may=doc.metadata.get("may"),
            jun=doc.metadata.get("jun"),
            jul=doc.metadata.get("jul"),
            aug=doc.metadata.get("aug"),
            sep=doc.metadata.get("sep"),
            oct=doc.metadata.get("oct"),
            nov=doc.metadata.get("nov"),
            dec=doc.metadata.get("dec"),
            safety=doc.metadata.get("safety"),
            nature=doc.metadata.get("nature"),
            hiking=doc.metadata.get("hiking"),
            beach=doc.metadata.get("beach"),
            watersports=doc.metadata.get("watersports"),
            entertainment=doc.metadata.get("entertainment"),
            wintersports=doc.metadata.get("wintersports"),
            culture=doc.metadata.get("culture"),
            culinary=doc.metadata.get("culinary"),
            architecture=doc.metadata.get("architecture"),
            shopping=doc.metadata.get("shopping"),
            description=doc.metadata.get("description"),
        )
