import re

from django.conf import settings

from rag.schemas import Chunk


def clean_text(text: str) -> str:
    cleaned = text.replace('\x00', ' ')
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned.strip()


def estimate_tokens(text: str) -> int:
    return max(1, len(text.split()))


def chunk_text(
    text: str,
    chunk_tokens: int | None = None,
    overlap_ratio: float | None = None,
) -> list[Chunk]:
    words = text.split()
    size = chunk_tokens or settings.RAG_CHUNK_TOKENS
    overlap = overlap_ratio if overlap_ratio is not None else settings.RAG_CHUNK_OVERLAP
    step = max(1, int(size * (1 - overlap)))
    chunks: list[Chunk] = []

    if not words:
        return chunks

    index = 0
    start = 0
    while start < len(words):
        end = min(len(words), start + size)
        content = ' '.join(words[start:end]).strip()
        if content:
            chunks.append(Chunk(index=index, content=content, token_count=estimate_tokens(content)))
            index += 1
        if end >= len(words):
            break
        start += step
    return chunks
