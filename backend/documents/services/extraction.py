import re
from pathlib import Path
from pypdf import PdfReader


class ExtractionError(ValueError):
    pass


def normalize_text(text: str) -> str:
    if not text:
        return ""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines).strip()


def extract_pdf_text(file_path_or_obj) -> str:
    text_parts = []
    try:
        reader = PdfReader(file_path_or_obj)
        for page_idx, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text_parts.append(f"--- Page {page_idx + 1} ---\n{page_text}")
    except Exception as exc:
        raise ExtractionError(f"Failed to read PDF file: {exc}") from exc

    text = normalize_text("\n".join(text_parts))
    if not text:
        raise ExtractionError("No selectable text found in this PDF.")

    return text


def extract_txt_text(file_obj) -> str:
    try:
        file_obj.open("rb")
        raw = file_obj.read()
    except Exception:
        if hasattr(file_obj, "read"):
            raw = file_obj.read()
        else:
            with open(file_obj, "rb") as f:
                raw = f.read()
    finally:
        try:
            file_obj.close()
        except Exception:
            pass

    if isinstance(raw, bytes):
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = raw.decode("latin-1", errors="replace")
    else:
        text = str(raw)

    text = normalize_text(text)
    if not text:
        raise ExtractionError("Text file is empty.")

    return text


def extract_docx_text(file_path) -> str:
    try:
        import docx
    except ImportError as exc:
        raise ExtractionError(
            "python-docx is not installed. Run pip install python-docx."
        ) from exc

    try:
        doc = docx.Document(file_path)
        text_parts = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text.strip())
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        text_parts.append(cell.text.strip())
        text = normalize_text("\n".join(text_parts))
    except Exception as exc:
        raise ExtractionError(f"Failed to extract DOCX text: {exc}") from exc

    if not text:
        raise ExtractionError("DOCX file contains no readable text.")
    return text


def extract_image_text(file_path) -> str:
    """Attempts OCR extraction using pytesseract/PIL, falls back gracefully."""
    try:
        from PIL import Image
    except ImportError:
        raise ExtractionError("PIL library is missing. Install Pillow to process images.")

    try:
        img = Image.open(file_path)
        # Try pytesseract OCR if system binary exists
        try:
            import pytesseract
            ocr_text = pytesseract.image_to_string(img)
            text = normalize_text(ocr_text)
            if text:
                return text
        except Exception:
            pass

        # Fallback metadata representation
        return normalize_text(
            f"Image File: {Path(file_path).name}\n"
            f"Format: {img.format}, Size: {img.size[0]}x{img.size[1]}px, Mode: {img.mode}\n"
            "Visual image document ingested into MemoryOS."
        )
    except Exception as exc:
        raise ExtractionError(f"Failed to process image file: {exc}") from exc


def extract_link_text(url: str) -> str:
    """Fetches web page content and strips HTML tags."""
    if not url:
        raise ExtractionError("Link URL is missing.")

    try:
        import requests

        response = requests.get(url, timeout=10, headers={"User-Agent": "MemoryOS/1.0"})
        response.raise_for_status()

        html = response.text
        # Simple HTML tag stripping
        clean_text = re.sub(r"<script.*?>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
        clean_text = re.sub(r"<style.*?>.*?</style>", "", clean_text, flags=re.DOTALL | re.IGNORECASE)
        clean_text = re.sub(r"<[^>]+>", " ", clean_text)
        clean_text = re.sub(r"\s+", " ", clean_text)

        text = normalize_text(clean_text)
        if not text:
            raise ExtractionError(f"No text content found at URL: {url}")
        return text
    except Exception as exc:
        raise ExtractionError(f"Failed to fetch content from URL ({url}): {exc}") from exc


def extract_document_text(document) -> str:
    if document.file_type == "note":
        text = normalize_text(document.raw_text or "")
        if not text:
            raise ExtractionError("Note content is empty.")
        return text

    if document.file_type == "pdf":
        return extract_pdf_text(document.file.path)

    if document.file_type in {"txt", "md"}:
        return extract_txt_text(document.file)

    if document.file_type == "docx":
        return extract_docx_text(document.file.path)

    if document.file_type == "image":
        return extract_image_text(document.file.path)

    if document.file_type == "link":
        if document.raw_text and document.raw_text.strip():
            return normalize_text(document.raw_text)
        return extract_link_text(document.source_url)

    raise ExtractionError(f"Unsupported document type: {document.file_type}")
