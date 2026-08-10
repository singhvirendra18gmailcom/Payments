from unittest.mock import patch


FAKE_EMBEDDING = [0.01] * 768


@patch(
    "app.ai.embedding_service."
    "GeminiEmbeddingService.generate_document_embedding"
)
def test_generate_embeddings(
    mock_embedding,
    client,
):

    mock_embedding.return_value = FAKE_EMBEDDING

    content = (
        "PACS.008 handles customer credit transfers. "
        * 100
    ).encode()

    upload = client.post(
        "/documents/upload",
        files={
            "file": (
                "payment.txt",
                content,
                "text/plain",
            )
        },
    )

    document_id = upload.json()["id"]

    client.post(
        f"/documents/{document_id}/process"
    )

    client.post(
        f"/documents/{document_id}/chunks",
        json={
            "chunk_size": 500,
            "chunk_overlap": 50,
        },
    )

    response = client.post(
        f"/documents/{document_id}/embeddings"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["embedded_chunks"] > 0
    assert body["failed_chunks"] == 0

    for embedding in body["embeddings"]:
        assert (
            embedding["embedding_status"]
            == "completed"
        )
        assert (
            embedding["embedding_dimension"]
            == 768
        )