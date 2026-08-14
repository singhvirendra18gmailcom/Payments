from unittest.mock import patch

from app.vector_store.models import (
    VectorSearchMatch,
    VectorSearchResult,
)


@patch(
    "app.ai.rag_service."
    "GeminiRAGService.generate_answer"
)
@patch(
    "app.documents.service."
    "search_document_chunks"
)
def test_ask_document(
    mock_search,
    mock_generate_answer,
    client,
):

    mock_search.return_value = VectorSearchResult(
        collection_name="payment_document_chunks",
        matches=[
            VectorSearchMatch(
                vector_id="document-1-chunk-1",
                document_text=(
                    "PACS.008 is an ISO 20022 "
                    "customer credit transfer message."
                ),
                metadata={
                    "document_id": 1,
                    "chunk_id": 1,
                    "chunk_order": 1,
                    "user_id": 1,
                },
                distance=0.08,
            )
        ],
    )

    mock_generate_answer.return_value = (
        "PACS.008 is an ISO 20022 message "
        "used for customer credit transfers."
    )

    response = client.post(
        "/documents/1/ask",
        json={
            "question": "What is PACS.008?",
            "top_k": 5,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["document_id"] == 1

    assert "ISO 20022" in body["answer"]

    assert body["total_sources"] == 1

    assert (
        body["sources"][0]["chunk_id"]
        == 1
    )

    mock_generate_answer.assert_called_once()