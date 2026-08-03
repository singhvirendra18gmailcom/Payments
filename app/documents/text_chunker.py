from dataclasses import dataclass


@dataclass
class TextChunk:
    order: int
    text: str
    character_count: int
    word_count: int


def split_text_into_chunks(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
) -> list[TextChunk]:
    """
    Split text into overlapping character-based chunks.

    Args:
        text: Extracted document text.
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Characters repeated between neighboring chunks.

    Returns:
        Ordered list of TextChunk objects.
    """

    if not text or not text.strip():
        raise ValueError("Text cannot be empty.")

    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero.")

    if chunk_overlap < 0:
        raise ValueError("Chunk overlap cannot be negative.")

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "Chunk overlap must be smaller than chunk size."
        )

    cleaned_text = normalize_text(text)

    chunks: list[TextChunk] = []
    start = 0
    order = 1
    text_length = len(cleaned_text)

    while start < text_length:
        tentative_end = min(start + chunk_size, text_length)
        end = find_best_split_position(
            text=cleaned_text,
            start=start,
            tentative_end=tentative_end,
        )

        chunk_text = cleaned_text[start:end].strip()

        if chunk_text:
            chunks.append(
                TextChunk(
                    order=order,
                    text=chunk_text,
                    character_count=len(chunk_text),
                    word_count=len(chunk_text.split()),
                )
            )
            order += 1

        if end >= text_length:
            break

        start = max(0, end - chunk_overlap)
    return chunks


def normalize_text(text: str) -> str:
    """
    Remove excessive whitespace while preserving readable paragraphs.
    """

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    return "\n".join(lines)


def find_best_split_position(
    text: str,
    start: int,
    tentative_end: int,
) -> int:
    """
    Try to avoid splitting in the middle of a sentence or word.
    """

    if tentative_end >= len(text):
        return len(text)

    search_start = max(
        start,
        tentative_end - 200,
    )

    candidate_text = text[search_start:tentative_end]

    separators = (
        "\n\n",
        "\n",
        ". ",
        "? ",
        "! ",
        " ",
    )

    for separator in separators:
        position = candidate_text.rfind(separator)

        if position != -1:
            return search_start + position + len(separator)

    return tentative_end