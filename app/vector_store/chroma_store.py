from collections.abc import Sequence
from typing import Any

import chromadb
from chromadb.api.models.Collection import Collection

from app.vector_store.config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_PERSIST_DIRECTORY,
    VECTOR_STORE_BATCH_SIZE,
)
from app.vector_store.models import (
    VectorRecord,
    VectorSearchMatch,
    VectorSearchResult,
    VectorStoreResult,
)


class VectorStoreError(Exception):
    """Raised when a vector-store operation fails."""


class ChromaVectorStore:
    def __init__(self) -> None:
        CHROMA_PERSIST_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:
            self.client = chromadb.PersistentClient(
                path=str(CHROMA_PERSIST_DIRECTORY)
            )

            self.collection: Collection = (
                self.client.get_or_create_collection(
                    name=CHROMA_COLLECTION_NAME,
                    metadata={
                        "description": (
                            "AI Payment Assistant document chunks"
                        )
                    },
                )
            )

        except Exception as exc:
            raise VectorStoreError(
                "Could not initialize ChromaDB."
            ) from exc

    @property
    def collection_name(self) -> str:
        return self.collection.name

    def upsert_records(
        self,
        records: Sequence[VectorRecord],
    ) -> VectorStoreResult:
        """
        Insert new records or update existing records.

        Reusing the same vector ID makes this operation idempotent.
        """

        if not records:
            raise VectorStoreError(
                "No vector records were supplied."
            )

        stored_ids: list[str] = []

        try:
            for start in range(
                0,
                len(records),
                VECTOR_STORE_BATCH_SIZE,
            ):
                batch = records[
                    start : start + VECTOR_STORE_BATCH_SIZE
                ]

                ids = [record.vector_id for record in batch]
                embeddings = [
                    record.embedding for record in batch
                ]
                documents = [
                    record.document_text for record in batch
                ]
                metadatas = [
                    self._sanitize_metadata(record.metadata)
                    for record in batch
                ]

                self.collection.upsert(
                    ids=ids,
                    embeddings=embeddings,
                    documents=documents,
                    metadatas=metadatas,
                )

                stored_ids.extend(ids)

            return VectorStoreResult(
                collection_name=self.collection.name,
                stored_count=len(stored_ids),
                vector_ids=stored_ids,
            )

        except Exception as exc:
            raise VectorStoreError(
                "Could not store vectors in ChromaDB."
            ) from exc

    def get_records(
        self,
        vector_ids: list[str],
        include_embeddings: bool = False,
    ) -> dict[str, Any]:
        if not vector_ids:
            return {
                "ids": [],
                "documents": [],
                "metadatas": [],
            }

        include = [
            "documents",
            "metadatas",
        ]

        if include_embeddings:
            include.append("embeddings")

        try:
            return self.collection.get(
                ids=vector_ids,
                include=include,
            )

        except Exception as exc:
            raise VectorStoreError(
                "Could not retrieve vectors from ChromaDB."
            ) from exc

    def count_document_vectors(
        self,
        *,
        document_id: int,
        user_id: int,
    ) -> int:
        try:
            result = self.collection.get(
                where={
                    "$and": [
                        {"document_id": document_id},
                        {"user_id": user_id},
                    ]
                },
                include=[],
            )

            return len(result.get("ids", []))

        except Exception as exc:
            raise VectorStoreError(
                "Could not count document vectors."
            ) from exc

    def delete_document_vectors(
        self,
        *,
        document_id: int,
        user_id: int,
    ) -> None:
        try:
            self.collection.delete(
                where={
                    "$and": [
                        {"document_id": document_id},
                        {"user_id": user_id},
                    ]
                }
            )

        except Exception as exc:
            raise VectorStoreError(
                "Could not delete document vectors."
            ) from exc

    @staticmethod
    def _sanitize_metadata(
        metadata: dict[str, Any],
    ) -> dict[str, str | int | float | bool]:
        """
        Keep metadata values compatible with Chroma filters.
        """

        sanitized: dict[
            str,
            str | int | float | bool,
        ] = {}

        for key, value in metadata.items():
            if value is None:
                continue

            if isinstance(
                value,
                (str, int, float, bool),
            ):
                sanitized[key] = value
            else:
                sanitized[key] = str(value)

        return sanitized

    def search_similar_chunks(
        self,
        *,
        query_embedding: list[float],
        document_id: int,
        user_id: int,
        top_k: int = 5,
    ) -> VectorSearchResult:
        """
        Search for chunks closest to the supplied query embedding.
        """

        if not query_embedding:
            raise VectorStoreError(
                "Query embedding cannot be empty."
            )

        if top_k <= 0:
            raise VectorStoreError(
                "top_k must be greater than zero."
            )

        try:
            result = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where={
                    "$and": [
                        {"document_id": document_id},
                        {"user_id": user_id},
                    ]
                },
                include=[
                    "documents",
                    "metadatas",
                    "distances",
                ],
            )

            ids = (
                result.get("ids", [[]])[0]
                if result.get("ids")
                else []
            )

            documents = (
                result.get("documents", [[]])[0]
                if result.get("documents")
                else []
            )

            metadatas = (
                result.get("metadatas", [[]])[0]
                if result.get("metadatas")
                else []
            )

            distances = (
                result.get("distances", [[]])[0]
                if result.get("distances")
                else []
            )

            matches: list[VectorSearchMatch] = []

            for vector_id, document_text, metadata, distance in zip(
                ids,
                documents,
                metadatas,
                distances,
            ):
                if document_text is None:
                    continue

                matches.append(
                    VectorSearchMatch(
                        vector_id=vector_id,
                        document_text=document_text,
                        metadata=metadata or {},
                        distance=float(distance),
                    )
                )

            return VectorSearchResult(
                collection_name=self.collection.name,
                matches=matches,
            )

        except Exception as exc:
            raise VectorStoreError(
                "Semantic search failed in ChromaDB."
            ) from exc