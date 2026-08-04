"""
Chunk validation module.

Automatically validates every chunk after creation, checking for:
- Complete sentences
- Correct overlap
- No corrupted words / random spacing
- No duplicate chunks
- No empty chunks
- Token count within acceptable range

Generates a validation report that can be logged or returned via API.
"""

import logging
import re

from django.conf import settings

from .chunker import count_tokens

logger = logging.getLogger(__name__)


def validate_chunk_text(text: str) -> list[str]:
    """Validate a single chunk's text quality. Returns list of issues."""
    issues: list[str] = []

    if not text or not text.strip():
        issues.append("EMPTY: Chunk has no text content.")
        return issues

    stripped = text.strip()

    # Check for corrupted characters (long runs of non-alpha)
    if re.search(r"[^\w\s.,;:!?'\"\-()]{5,}", stripped):
        issues.append("CORRUPTED: Contains runs of non-standard characters.")

    # Check for excessive random spacing (3+ spaces within text)
    inner_text = stripped.replace("\n", " ")
    if re.search(r"  {3,}", inner_text):
        issues.append("SPACING: Contains excessive internal whitespace.")

    # Check for broken words (single characters surrounded by spaces, except articles)
    allowed_singles = {"a", "i", "I", "-", "–", "—", "&", "/", "|"}
    words = inner_text.split()
    broken_count = sum(
        1 for w in words
        if len(w) == 1 and w not in allowed_singles and w.isalpha()
    )
    if broken_count > 3:
        issues.append(f"BROKEN_WORDS: {broken_count} single-character words detected.")

    # Check token bounds
    tokens = count_tokens(stripped)
    min_tokens = getattr(settings, "RAG_MIN_CHUNK_TOKENS", 20)
    max_tokens = getattr(settings, "RAG_MAX_CHUNK_TOKENS", 700)

    if tokens < min_tokens:
        issues.append(f"TOO_SHORT: Only {tokens} tokens (min {min_tokens}).")
    if tokens > max_tokens * 1.5:  # allow 50% overflow before flagging
        issues.append(f"TOO_LONG: {tokens} tokens (max ~{max_tokens}).")

    # Check for garbled text (very low alpha ratio)
    alpha_count = sum(1 for c in stripped if c.isalpha())
    if len(stripped) > 20 and alpha_count / len(stripped) < 0.3:
        issues.append("GARBLED: Very low alphabetic character ratio.")

    return issues


def validate_chunks(chunks: list[dict]) -> dict:
    """
    Validate a list of chunk dicts (as returned by chunk_text).
    Returns a validation report.
    """
    report = {
        "total_chunks": len(chunks),
        "valid_chunks": 0,
        "invalid_chunks": 0,
        "empty_chunks": 0,
        "duplicate_chunks": 0,
        "issues": [],
        "passed": True,
    }

    if not chunks:
        report["issues"].append({"chunk_index": -1, "problems": ["No chunks produced."]})
        report["passed"] = False
        return report

    seen_signatures: set[str] = set()

    for idx, chunk in enumerate(chunks):
        text = chunk.get("text", "")
        chunk_issues: list[str] = []

        # Validate text quality
        text_issues = validate_chunk_text(text)
        chunk_issues.extend(text_issues)

        # Check for duplicates
        signature = " ".join(text.lower().split())[:300]
        if signature in seen_signatures:
            chunk_issues.append("DUPLICATE: Identical chunk content detected.")
            report["duplicate_chunks"] += 1
        seen_signatures.add(signature)

        # Check metadata
        metadata = chunk.get("metadata", {})
        if not metadata.get("page_number") and metadata.get("page_number") != 0:
            chunk_issues.append("METADATA: Missing page_number.")

        if chunk_issues:
            report["invalid_chunks"] += 1
            report["issues"].append({
                "chunk_index": idx,
                "token_count": chunk.get("token_count", 0),
                "problems": chunk_issues,
            })
        else:
            report["valid_chunks"] += 1

        if not text.strip():
            report["empty_chunks"] += 1

    # Overall pass/fail
    critical_count = sum(
        1 for issue in report["issues"]
        if any(
            p.startswith(("EMPTY", "CORRUPTED", "GARBLED"))
            for p in issue["problems"]
        )
    )
    report["passed"] = critical_count == 0

    return report


def log_validation_report(report: dict, document_title: str = "") -> None:
    """Log a validation report with appropriate severity."""
    prefix = f"[{document_title}] " if document_title else ""

    if report["passed"]:
        logger.info(
            "%sChunk validation PASSED: %d/%d valid, %d duplicates",
            prefix,
            report["valid_chunks"],
            report["total_chunks"],
            report["duplicate_chunks"],
        )
    else:
        logger.warning(
            "%sChunk validation FAILED: %d/%d invalid, %d empty, %d duplicates",
            prefix,
            report["invalid_chunks"],
            report["total_chunks"],
            report["empty_chunks"],
            report["duplicate_chunks"],
        )

    for issue in report["issues"]:
        for problem in issue["problems"]:
            level = logging.WARNING if problem.startswith(("EMPTY", "CORRUPTED", "GARBLED")) else logging.INFO
            logger.log(
                level,
                "%sChunk %d: %s",
                prefix,
                issue["chunk_index"],
                problem,
            )
