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
        # TODO: split into sentences, group into chunks
        if not text:
            return []
        # Tách câu bằng Regex (dựa trên dấu chấm, chấm than, hỏi chấm)
        sentences = re.split(r'(?<=[.!?])\s+|\n+', text.strip())
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            chunk = " ".join(sentences[i:i + self.max_sentences_per_chunk])
            chunks.append(chunk)
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
        # TODO: implement recursive splitting strategy
        return self._split(text, self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        # TODO: recursive helper used by RecursiveChunker.chunk
        # Nếu chuỗi đủ ngắn, trả về luôn
        if len(current_text) <= self.chunk_size or not remaining_separators:
            return [current_text]

        # Lấy dấu phân cách đầu tiên
        separator = remaining_separators[0]
        next_separators = remaining_separators[1:]

        # Cắt chuỗi bằng dấu phân cách
        # Nếu separator rỗng (""), cắt theo từng ký tự (hoặc fallback)
        if separator == "":
            parts = [current_text[i:i+self.chunk_size] for i in range(0, len(current_text), self.chunk_size)]
        else:
            parts = current_text.split(separator)

        results = []
        for part in parts:
            if not part.strip():
                continue
            # Nếu đoạn cắt ra vẫn quá dài, gọi đệ quy với dấu phân cách tiếp theo
            if len(part) > self.chunk_size:
                results.extend(self._split(part, next_separators))
            else:
                results.append(part)
        
        return results


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    # TODO: implement cosine similarity formula
    dot_product = _dot(vec_a, vec_b)
    norm_a = math.sqrt(sum(x * x for x in vec_a))
    norm_b = math.sqrt(sum(x * x for x in vec_b))
    
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
        
    return dot_product / (norm_a * norm_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        # TODO: call each chunker, compute stats, return comparison dict
        fixed = FixedSizeChunker(chunk_size=chunk_size, overlap=20).chunk(text)
        sentence = SentenceChunker(max_sentences_per_chunk=2).chunk(text)
        recursive = RecursiveChunker(chunk_size=chunk_size).chunk(text)

        return {
            'fixed_size': {'count': len(fixed), 'avg_length': sum(len(c) for c in fixed)/(len(fixed) or 1), 'chunks': fixed},
            'by_sentences': {'count': len(sentence), 'avg_length': sum(len(c) for c in sentence)/(len(sentence) or 1), 'chunks': sentence},
            'recursive': {'count': len(recursive), 'avg_length': sum(len(c) for c in recursive)/(len(recursive) or 1), 'chunks': recursive}
        }
