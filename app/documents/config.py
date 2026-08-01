from pathlib import Path


UPLOAD_DIRECTORY = Path("uploads/documents")

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".txt",
}

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "text/plain",
}

READ_CHUNK_SIZE = 1024 * 1024  # 1 MB