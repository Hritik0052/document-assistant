from django.conf import settings

from rag.client import openrouter_client
from rag.schemas import Chunk


async def embed_texts(texts: list[str]) -> list[list[float]]:
    client = openrouter_client()
    vectors: list[list[float]] = []
    batch_size = 16
    for offset in range(0, len(texts), batch_size):
        batch = texts[offset:offset + batch_size]
        response = await client.embeddings.create(
            model=settings.OPENROUTER_EMBEDDING_MODEL,
            input=batch,
            encoding_format='float',
        )
        ordered = sorted(response.data, key=lambda item: item.index)
        vectors.extend(item.embedding for item in ordered)
    return vectors


async def embed_chunks(chunks: list[Chunk]) -> list[list[float]]:
    return await embed_texts([chunk.content for chunk in chunks])
