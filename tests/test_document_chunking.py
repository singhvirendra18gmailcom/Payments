def test_document_chunking(client):

    content = (
        "PACS.008 customer credit transfer settlement information. "
        * 100
    ).encode()

    upload = client.post(
        "/documents/upload",
        files={
            "file": (
                "large-payment.txt",
                content,
                "text/plain",
            )
        },
    )

    document_id = upload.json()["id"]

    process = client.post(
        f"/documents/{document_id}/process"
    )

    assert process.status_code == 200

    response = client.post(
        f"/documents/{document_id}/chunks",
        json={
            "chunk_size": 500,
            "chunk_overlap": 50,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total_chunks"] > 1
    assert body["processing_status"] == "chunked"

    chunks_response = client.get(
        f"/documents/{document_id}/chunks"
    )

    assert chunks_response.status_code == 200

    chunks = chunks_response.json()["chunks"]

    assert len(chunks) == body["total_chunks"]

    assert chunks[0]["chunk_order"] == 1