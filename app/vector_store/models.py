from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class VectorRecord:
    vector_id: str
    embedding: list[float]
    document_text: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class VectorStoreResult:
    collection_name: str
    stored_count: int
    vector_ids: list[str]