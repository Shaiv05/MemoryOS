from pypdf import PdfReader


class ExtractionError(ValueError):
    pass


def normalize_text(text):
    return "\n".join(line.strip() for line in text.splitlines() if line.strip()).strip()


def extract_pdf_text(file_path):
    text_parts = []
    reader = PdfReader(file_path)

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)

    text = normalize_text("\n".join(text_parts))
    if not text:
        raise ExtractionError("No selectable text found in this PDF.")

    return text


def extract_txt_text(file_obj):
    file_obj.open("rb")
    try:
        raw = file_obj.read()
    finally:
        file_obj.close()

    if isinstance(raw, bytes):
        text = raw.decode("utf-8", errors="replace")
    else:
        text = raw

    text = normalize_text(text)
    if not text:
        raise ExtractionError("Text file is empty.")

    return text


def extract_document_text(document):
    if document.file_type == "note":
        text = normalize_text(document.raw_text or "")
        if not text:
            raise ExtractionError("Note is empty.")
        return text

    if document.file_type == "pdf":
        return extract_pdf_text(document.file.path)

    if document.file_type == "txt":
        return extract_txt_text(document.file)

    if document.file_type == "link":
        raise ExtractionError("Link extraction is not implemented in this MVP yet.")

    raise ExtractionError(f"Unsupported document type: {document.file_type}")
