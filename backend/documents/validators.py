from pathlib import Path

from django.conf import settings
from rest_framework import serializers


SUPPORTED_FILE_TYPES = {"note", "pdf", "txt", "docx", "md", "image", "link"}
SUPPORTED_UPLOAD_EXTENSIONS = {
    "pdf": {".pdf"},
    "txt": {".txt", ".log"},
    "docx": {".docx", ".doc"},
    "md": {".md", ".markdown"},
    "image": {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"},
}


def validate_document_input(attrs, instance=None):
    file_type = attrs.get("file_type", getattr(instance, "file_type", None))
    file = attrs.get("file", getattr(instance, "file", None))
    raw_text = attrs.get("raw_text", getattr(instance, "raw_text", ""))
    source_url = attrs.get("source_url", getattr(instance, "source_url", ""))

    if file_type not in SUPPORTED_FILE_TYPES:
        raise serializers.ValidationError(
            {"file_type": "Supported types are note, pdf, txt, docx, md, image, and link."}
        )

    if file and getattr(file, "size", 0) > settings.MAX_DOCUMENT_UPLOAD_SIZE:
        max_mb = settings.MAX_DOCUMENT_UPLOAD_SIZE // (1024 * 1024)
        raise serializers.ValidationError(
            {"file": f"File is too large. Maximum size allowed is {max_mb}MB."}
        )

    if file_type == "note" and not str(raw_text or "").strip() and not file:
        raise serializers.ValidationError({"raw_text": "Notes require text content."})

    if file_type in {"pdf", "txt", "docx", "md", "image"}:
        if not file:
            raise serializers.ValidationError({"file": f"{file_type.upper()} documents require a file."})

        extension = Path(file.name).suffix.lower()
        if extension not in SUPPORTED_UPLOAD_EXTENSIONS.get(file_type, set()):
            allowed = ", ".join(SUPPORTED_UPLOAD_EXTENSIONS.get(file_type, []))
            raise serializers.ValidationError(
                {"file": f"Expected a {file_type.upper()} file ({allowed})."}
            )

    if file_type == "link" and not source_url:
        raise serializers.ValidationError({"source_url": "Links require a source URL."})

    return attrs
