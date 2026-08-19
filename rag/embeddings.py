import asyncio
import logging

from django.conf import settings

from rag.client import openrouter_client
from rag.schemas import Chunk

logger = logging.getLogger(__name__)


async def embed_texts(texts: list[str]) -> list[list[float]]:
    client = openrouter_client()
    vectors: list[list[float]] = []
    batch_size = 16
    total = len(texts)
    for offset in range(0, total, batch_size):
        batch = texts[offset:offset + batch_size]
        logger.info('Embedding batch %s-%s of %s', offset + 1, offset + len(batch), total)
        for attempt in range(1, 4):
            try:
                response = await client.embeddings.create(
                    model=settings.OPENROUTER_EMBEDDING_MODEL,
                    input=batch,
                    encoding_format='float',
                )
                break
            except Exception as exc:
                if attempt == 3 or '429' not in str(exc):
                    raise
                wait = attempt * 5
                logger.warning('Rate limited, retrying in %ss (attempt %s/3)', wait, attempt)
                await asyncio.sleep(wait)
        ordered = sorted(response.data, key=lambda item: item.index)
        vectors.extend(item.embedding for item in ordered)
    return vectors


async def embed_chunks(chunks: list[Chunk]) -> list[list[float]]:
    return await embed_texts([chunk.content for chunk in chunks])
