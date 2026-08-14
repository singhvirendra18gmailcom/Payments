from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from app.documents.extraction import ExtractionResult


class DocumentExtractionError(Exception):
    """Raised when document text extraction fails."""


def extract_text_from_pdf(file_path: Path) -> ExtractionResult:
    """
    Extract text from a text-based PDF.

    Args:
        file_path: Physical path of the saved PDF.

    Returns:
        ExtractionResult containing text and page count.

    Raises:
        DocumentExtractionError: If the PDF is invalid, encrypted,
        unreadable, or contains no extractable text.
    """

    try:
        reader = PdfReader(str(file_path))

        if reader.is_encrypted:
            try:
                unlock_result = reader.decrypt("")
            except Exception as exc:
                raise DocumentExtractionError(
                    "Encrypted PDF files are not supported."
                ) from exc

            if unlock_result == 0:
                raise DocumentExtractionError(
                    "Password-protected PDF files are not supported."
                )

        page_texts: list[str] = []

        for page_number, page in enumerate(reader.pages, start=1):
            try:
                extracted_page_text = page.extract_text() or ""
            except Exception as exc:
                raise DocumentExtractionError(
                    f"Text extraction failed on PDF page {page_number}."
                ) from exc

            cleaned_page_text = extracted_page_text.strip()

            if cleaned_page_text:
                page_texts.append(
                    f"--- Page {page_number} ---\n{cleaned_page_text}"
                )

        combined_text = "\n\n".join(page_texts).strip()

        if not combined_text:
            raise DocumentExtractionError(
                "No text could be extracted. "
                "The PDF may be scanned or image-based."
            )

        return ExtractionResult(
            text=combined_text,
            page_count=len(reader.pages),
        )

    except DocumentExtractionError:
        raise

    except PdfReadError as exc:
        raise DocumentExtractionError(
            "The uploaded PDF is invalid or corrupted."
        ) from exc

    except OSError as exc:
        raise DocumentExtractionError(
            "The PDF file could not be opened."
        ) from exc

    except Exception as exc:
        raise DocumentExtractionError(
            "An unexpected error occurred while reading the PDF."
        ) from exc


def extract_text_from_txt(file_path: Path) -> ExtractionResult:
    """
    Extract text from a TXT file.

    Attempts UTF-8 first, then UTF-8 with BOM, and finally Windows-1252.
    """

    encodings = (
        "utf-8",
        "utf-8-sig",
        "cp1252",
    )

    decoded_text: str | None = None

    for encoding in encodings:
        try:
            decoded_text = file_path.read_text(encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
        except OSError as exc:
            raise DocumentExtractionError(
                "The TXT file could not be opened."
            ) from exc

    if decoded_text is None:
        raise DocumentExtractionError(
            "The TXT file encoding is not supported."
        )

    cleaned_text = decoded_text.strip()

    if not cleaned_text:
        raise DocumentExtractionError(
            "The TXT file does not contain any text."
        )

    return ExtractionResult(
        text=cleaned_text,
        page_count=None,
    )


def extract_document_text(
    file_path: str,
    file_extension: str,
) -> ExtractionResult:
    """
    Select the correct extractor according to the file extension.
    """

    path = Path(file_path)

    if not path.exists():
        raise DocumentExtractionError(
            "The stored document file was not found."
        )

    normalized_extension = file_extension.lower()

    if normalized_extension == ".pdf":
        return extract_text_from_pdf(path)

    if normalized_extension == ".txt":
        return extract_text_from_txt(path)

    raise DocumentExtractionError(
        f"Text extraction is not supported for {normalized_extension} files."
    )