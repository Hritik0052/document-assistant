from django.conf import settings

from rag.schemas import Chunk


async def embed_texts(texts: list[str]) -> list[list[float]]:
    if not settings.OPENAI_CONFIGURED:
        raise RuntimeError(
            'OPENAI_API_KEY is not set. Add it to your .env to generate embeddings.'
        )

    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    vectors: list[list[float]] = []
    batch_size = 64
    for offset in range(0, len(texts), batch_size):
        batch = texts[offset:offset + batch_size]
        response = await client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=batch,
        )
        ordered = sorted(response.data, key=lambda item: item.index)
        vectors.extend(item.embedding for item in ordered)
    return vectors


async def embed_chunks(chunks: list[Chunk]) -> list[list[float]]:
    return await embed_texts([chunk.content for chunk in chunks])
