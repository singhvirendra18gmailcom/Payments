from unittest.mock import patch

from app.vector_store.models import VectorStoreResult

@patch(
    "app.vector_store.chroma_store."
    "ChromaVectorStore.upsert_records"
)
def test_vector_indexing(
    mock_upsert,
    client,
    embedded_document,
):
    mock_upsert.return_value = VectorStoreResult(
        collection_name="test_collection",
        stored_count=1,
        vector_ids=[
            f"document-{embedded_document}-chunk-1"
        ],
    )

    response = client.post(
        f"/documents/{embedded_document}/vectors"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["processing_status"] == "indexed"
    assert body["indexed_chunks"] >= 1

    mock_upsert.assert_called_once()