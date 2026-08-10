from unittest.mock import patch

from app.vector_store.models import (
    VectorSearchMatch,
    VectorSearchResult,
)

@patch(
    "app.vector_store.chroma_store."
    "ChromaVectorStore.search_similar_chunks"
)
@patch(
    "app.ai.embedding_service."
    "GeminiEmbeddingService.generate_query_embedding"
)
def test_semantic_search(
    mock_query_embedding,
    mock_search,
    client,
    indexed_document,
):
    mock_query_embedding.return_value = (
        [0.01] * 768
    )

    mock_search.return_value = VectorSearchResult(
        collection_name="payment_document_chunks",
        matches=[
            VectorSearchMatch(
                vector_id=(
                    f"document-{indexed_document}-chunk-1"
                ),
                document_text=(
                    "PACS.008 is used for "
                    "customer credit transfers."
                ),
                metadata={
                    "document_id": indexed_document,
                    "chunk_id": 1,
                    "chunk_order": 1,
                    "user_id": 1,
                },
                distance=0.10,
            )
        ],
    )

    response = client.post(
        f"/documents/{indexed_document}/search",
        json={
            "question": (
                "What is PACS.008 used for?"
            ),
            "top_k": 5,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total_matches"] == 1
    assert (
        "customer credit transfers"
        in body["matches"][0]["text"]
    )