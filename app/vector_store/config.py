import os
from pathlib import Path


CHROMA_PERSIST_DIRECTORY = Path(
    os.getenv(
        "CHROMA_PERSIST_DIRECTORY",
        "./data/chroma",
    )
)

CHROMA_COLLECTION_NAME = os.getenv(
    "CHROMA_COLLECTION_NAME",
    "payment_document_chunks",
)

VECTOR_STORE_BATCH_SIZE = int(
    os.getenv(
        "VECTOR_STORE_BATCH_SIZE",
        "100",
    )
)