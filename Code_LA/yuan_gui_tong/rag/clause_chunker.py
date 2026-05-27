"""Clause chunker: parse MinerU Markdown into structured clauses."""

import re
from typing import List


class Clause:
    def __init__(self, page_content: str, metadata: dict):
        self.page_content = page_content
        self.metadata = metadata


CLAUSE_PATTERNS = [
    re.compile(r"第(\d+(?:\.\d+)*)条"),
    re.compile(r"(?:^|\n)(\d+(?:\.\d+)+)\s"),
    re.compile(r"([IVX]+-\d+(?:\.\d+)*)"),
]

MANDATORY_KEYWORDS = ["必须", "严禁", "应", "不应", "不得", "禁止"]


def _detect_clause_number(text: str) -> str | None:
    for pat in CLAUSE_PATTERNS:
        m = pat.search(text)
        if m:
            return m.group(1)
    return None


def _is_mandatory(text: str) -> bool:
    return any(kw in text for kw in MANDATORY_KEYWORDS)


def _get_heading_level(line: str) -> int:
    m = re.match(r"^(#{1,6})\s", line)
    return len(m.group(1)) if m else 0


def _split_long_clause(content: str, max_chars: int = 3000) -> List[str]:
    if len(content) <= max_chars:
        return [content]

    parts = []
    paragraphs = content.split("\n\n")
    current = ""
    for para in paragraphs:
        if len(current) + len(para) > max_chars and current:
            parts.append(current.strip())
            current = para
        else:
            current += "\n\n" + para if current else para
    if current.strip():
        parts.append(current.strip())
    return parts


class ClauseChunker:
    def __init__(self, max_clause_chars: int = 3000):
        self.max_clause_chars = max_clause_chars

    def chunk_all(self, docs) -> List[Clause]:
        all_clauses = []
        for doc in docs:
            clauses = self._chunk_one(doc)
            all_clauses.extend(clauses)
        return all_clauses

    def _chunk_one(self, doc) -> List[Clause]:
        text = doc.full_markdown
        code = doc.standard_code
        name = doc.standard_name

        # Split by markdown headings to get hierarchy
        sections = re.split(r"\n(?=#{1,6}\s)", text)

        clauses = []
        current_heading = ""
        for section in sections:
            lines = section.split("\n", 1)
            first_line = lines[0]
            body = lines[1] if len(lines) > 1 else ""
            level = _get_heading_level(first_line)

            if level > 0:
                current_heading = re.sub(r"^#+\s*", "", first_line).strip()
                section_text = body
            else:
                section_text = section

            # Try to split by clause boundaries within this section
            sub_clauses = self._split_by_clause_boundaries(
                section_text, code, name, current_heading
            )
            clauses.extend(sub_clauses)

        # If no clauses found, fall back to heading-based chunks
        if not clauses:
            clauses = self._fallback_chunks(text, code, name)

        return clauses

    def _split_by_clause_boundaries(
        self, text: str, code: str, name: str, heading: str
    ) -> List[Clause]:
        """Split text at clause number boundaries."""
        # Find all clause number positions
        boundaries = []
        for pat in CLAUSE_PATTERNS:
            for m in pat.finditer(text):
                boundaries.append((m.start(), m.group(1)))

        if not boundaries:
            # No clause numbers found, treat as one chunk
            if text.strip():
                return self._make_clauses(text, code, name, heading, None)
            return []

        boundaries.sort()
        clauses = []
        for i, (pos, clause_num) in enumerate(boundaries):
            next_pos = boundaries[i + 1][0] if i + 1 < len(boundaries) else len(text)
            content = text[pos:next_pos].strip()
            clauses.extend(
                self._make_clauses(content, code, name, heading, clause_num)
            )

        # Add text before first boundary if meaningful
        if boundaries and boundaries[0][0] > 0:
            prefix = text[: boundaries[0][0]].strip()
            if prefix and len(prefix) > 20:
                clauses.insert(
                    0, Clause(prefix, {
                        "standard_code": code,
                        "standard_name": name,
                        "clause_number": "",
                        "heading": heading,
                        "is_mandatory": _is_mandatory(prefix),
                    })
                )

        return clauses

    def _make_clauses(
        self, content: str, code: str, name: str, heading: str, clause_num: str | None
    ) -> List[Clause]:
        parts = _split_long_clause(content, self.max_clause_chars)
        clauses = []
        for part in parts:
            suffix = f" (续)" if len(parts) > 1 and part != parts[0] else ""
            clauses.append(Clause(part, {
                "standard_code": code,
                "standard_name": name,
                "clause_number": (clause_num or "") + suffix,
                "heading": heading,
                "is_mandatory": _is_mandatory(part),
            }))
        return clauses

    def _fallback_chunks(self, text: str, code: str, name: str) -> List[Clause]:
        """Fallback: chunk by markdown headings as paragraph boundaries."""
        paragraphs = text.split("\n\n")
        clauses = []
        current = ""
        for para in paragraphs:
            if len(current) + len(para) > self.max_clause_chars and current:
                clauses.append(Clause(current.strip(), {
                    "standard_code": code,
                    "standard_name": name,
                    "clause_number": "",
                    "heading": "",
                    "is_mandatory": _is_mandatory(current),
                }))
                current = para
            else:
                current += "\n\n" + para if current else para
        if current.strip():
            clauses.append(Clause(current.strip(), {
                "standard_code": code,
                "standard_name": name,
                "clause_number": "",
                "heading": "",
                "is_mandatory": _is_mandatory(current),
            }))
        return clauses
