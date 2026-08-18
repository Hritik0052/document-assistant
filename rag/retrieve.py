import math

from django.conf import settings
from django.db import connection

from documents.models import Document, DocumentChunk
from rag.embeddings import embed_texts
from rag.schemas import RetrievedChunk


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right))
    norm_left = math.sqrt(sum(a * a for a in left))
    norm_right = math.sqrt(sum(b * b for b in right))
    if norm_left == 0 or norm_right == 0:
        return 0.0
    return dot / (norm_left * norm_right)


async def retrieve_chunks(document: Document, question: str) -> list[RetrievedChunk]:
    query_vectors = await embed_texts([question])
    query = query_vectors[0]
    top_k = settings.RAG_TOP_K
    min_similarity = settings.RAG_MIN_SIMILARITY

    if connection.vendor == 'postgresql':
        from pgvector.django import CosineDistance

        queryset = (
            DocumentChunk.objects.filter(document=document, embedding__isnull=False)
            .annotate(distance=CosineDistance('embedding', query))
            .order_by('distance')[:top_k]
        )
        retrieved: list[RetrievedChunk] = []
        async for chunk in queryset:
            similarity = 1 - float(chunk.distance)
            if similarity >= min_similarity:
                retrieved.append(
                    RetrievedChunk(
                        chunk_index=chunk.chunk_index,
                        content=chunk.content,
                        similarity=similarity,
                    )
                )
        return retrieved

    scored: list[RetrievedChunk] = []
    async for chunk in DocumentChunk.objects.filter(document=document).exclude(embedding=None):
        similarity = _cosine_similarity(query, chunk.embedding or [])
        if similarity >= min_similarity:
            scored.append(
                RetrievedChunk(
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    similarity=similarity,
                )
            )
    scored.sort(key=lambda item: item.similarity, reverse=True)
    return scored[:top_k]
