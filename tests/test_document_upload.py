def test_upload_txt_document(client):

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "payment.txt",
                b"PACS.008 is used for customer credit transfers.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 201

    body = response.json()


    assert body["id"] is not None
    assert body["original_filename"] == "payment.txt"
    assert body["content_type"] == "text/plain"
    assert body["processing_status"] == "uploaded"

def test_upload_rejects_unsupported_file(client):
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "picture.jpg",
                b"fake-data",
                "image/jpeg",
            )
        },
    )

    assert response.status_code in {400, 415}

def test_process_missing_document(client):

    response = client.post(
        "/documents/99999/process"
    )

    assert response.status_code == 404

def test_chunk_before_processing(
    client,
):

    upload = client.post(
        "/documents/upload",
        files={
            "file": (
                "test.txt",
                b"hello",
                "text/plain",
            )
        },
    )

    document_id = upload.json()["id"]

    response = client.post(
        f"/documents/{document_id}/chunks",
        json={
            "chunk_size": 500,
            "chunk_overlap": 50,
        },
    )

    assert response.status_code == 409

def test_search_unindexed_document(
    client,
    processed_document,
):

    response = client.post(
        f"/documents/{processed_document}/search",
        json={
            "question": "What is PACS.008?",
            "top_k": 5,
        },
    )

    assert response.status_code == 409


def test_user_cannot_access_missing_document(client):

    response = client.get(
        "/documents/999/text"
    )

    assert response.status_code == 404