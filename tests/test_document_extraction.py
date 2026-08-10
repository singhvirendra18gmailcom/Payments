def test_extract_txt_document(client):

    upload_response = client.post(
        "/documents/upload",
        files={
            "file": (
                "payment.txt",
                (
                    b"PACS.008 is an ISO 20022 "
                    b"customer credit transfer message."
                ),
                "text/plain",
            )
        },
    )

    assert upload_response.status_code == 201

    document_id = upload_response.json()["id"]

    response = client.post(
        f"/documents/{document_id}/process"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["processing_status"] == "completed"
    assert body["character_count"] > 0

    text_response = client.get(
        f"/documents/{document_id}/text"
    )

    assert text_response.status_code == 200

    extracted_text = text_response.json()[
        "extracted_text"
    ]

    assert "PACS.008" in extracted_text