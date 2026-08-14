from dataclasses import dataclass


@dataclass
class ExtractionResult:
    text: str
    page_count: int | None = None