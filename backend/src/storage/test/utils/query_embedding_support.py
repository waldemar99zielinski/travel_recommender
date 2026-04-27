from __future__ import annotations

from collections.abc import Sequence

from embeddings.protocols import TextEmbeddingModelProtocol


class KeywordTextEmbeddingModel(TextEmbeddingModelProtocol):
    """Deterministic keyword embedding model for semantic ranking tests."""

    _TOKEN_GROUPS: tuple[tuple[str, ...], ...] = (
        ("beach", "coast", "island", "tropical", "sea", "snorkel", "watersport"),
        ("mountain", "alpine", "hike", "trail", "nature"),
        ("ski", "snow", "winter", "snowboard"),
        ("culture", "museum", "history", "architecture", "art"),
        ("city", "nightlife", "shopping", "urban"),
        ("budget", "cheap", "affordable", "low-cost"),
        ("luxury", "premium", "exclusive", "five-star", "resort"),
        ("food", "culinary", "restaurant", "cuisine"),
    )

    def check_health(self) -> bool:
        return True

    def get_dimentions(self) -> int:
        return len(self._TOKEN_GROUPS)

    def embed_query(self, text: str) -> list[float]:
        normalized_text = text.lower().strip()
        if not normalized_text:
            raise ValueError("text must not be empty")

        return [self._count_token_matches(normalized_text, token_group) for token_group in self._TOKEN_GROUPS]

    def _count_token_matches(self, text: str, token_group: Sequence[str]) -> float:
        return float(sum(text.count(token) for token in token_group))
