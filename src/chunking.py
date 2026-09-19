from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        # Tách câu dựa trên ranh giới . ! ? hoặc .\n
        # Regex tìm vị trí kết thúc câu: (?<=[.!?])(?=\s+|\n+|$)
        raw_sentences = re.split(r'(?<=[.!?])\s+|\n+', text.strip())
        sentences = [s.strip() for s in raw_sentences if s.strip()]

        if not sentences:
            return []

        chunks: list[str] = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            group = sentences[i : i + self.max_sentences_per_chunk]
            chunk_str = " ".join(group)
            chunks.append(chunk_str)

        return chunks

class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]
        return self._split(text, self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if not current_text:
            return []
        if len(current_text) <= self.chunk_size:
            return [current_text]
        if not remaining_separators:
            # Fallback nếu hết dấu phân cách: cắt theo chunk_size
            return [current_text[i : i + self.chunk_size] for i in range(0, len(current_text), self.chunk_size)]

        sep = remaining_separators[0]
        next_seps = remaining_separators[1:]

        if sep == "":
            return [current_text[i : i + self.chunk_size] for i in range(0, len(current_text), self.chunk_size)]

        splits = current_text.split(sep)
        final_chunks: list[str] = []
        accumulated = ""

        for part in splits:
            item = part if not accumulated else sep + part
            if len(accumulated) + len(item) <= self.chunk_size:
                accumulated += item
            else:
                if accumulated:
                    final_chunks.append(accumulated)
                    accumulated = ""
                
                # Nếu phần nhỏ này vẫn lớn hơn chunk_size, gọi đệ quy với separator tiếp theo
                if len(part) > self.chunk_size:
                    sub_chunks = self._split(part, next_seps)
                    final_chunks.extend(sub_chunks)
                else:
                    accumulated = part

        if accumulated:
            final_chunks.append(accumulated)

        return final_chunks

class HeadingChunker:
    """
    Split text into chunks based on Markdown headings (#, ##, ###)
    and uppercase section titles (e.g. THÔNG TIN CHUNG, CHỨC NĂNG NHIỆM VỤ).
    """

    def __init__(self, chunk_size: int = 500) -> None:
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        lines = text.split("\n")
        chunks: list[str] = []
        current: list[str] = []

        for line in lines:
            stripped = line.strip()
            is_heading = (
                stripped.startswith("#")
                or (stripped.isupper() and len(stripped) > 3 and not stripped.startswith("HTTP"))
            )
            if is_heading and current:
                chunk_str = "\n".join(current).strip()
                if chunk_str:
                    chunks.append(chunk_str)
                current = [line]
            else:
                current.append(line)

        if current:
            chunk_str = "\n".join(current).strip()
            if chunk_str:
                chunks.append(chunk_str)

        return chunks


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0

    dot_val = sum(x * y for x, y in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(x * x for x in vec_a))
    mag_b = math.sqrt(sum(y * y for y in vec_b))

    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0

    return dot_val / (mag_a * mag_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        fixed = FixedSizeChunker(chunk_size=chunk_size, overlap=20).chunk(text)
        sentences = SentenceChunker(max_sentences_per_chunk=3).chunk(text)
        recursive = RecursiveChunker(chunk_size=chunk_size).chunk(text)
        heading = HeadingChunker(chunk_size=chunk_size).chunk(text)

        def get_stats(chunks: list[str]) -> dict:
            cnt = len(chunks)
            avg_len = sum(len(c) for c in chunks) / cnt if cnt > 0 else 0.0
            return {"count": cnt, "avg_length": avg_len, "chunks": chunks}

        return {
            "fixed_size": get_stats(fixed),
            "by_sentences": get_stats(sentences),
            "recursive": get_stats(recursive),
            "heading": get_stats(heading),
        }