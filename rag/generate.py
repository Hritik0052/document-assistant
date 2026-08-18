from django.conf import settings

from rag.schemas import AnswerResult, RetrievedChunk

SYSTEM_PROMPT = (
    'You are a document Q&A assistant. Answer only from the provided context. '
    'If the context does not contain the answer, say "I don\'t know based on the uploaded document." '
    'Do not use outside knowledge. Be concise and cite chunk numbers when useful.'
)


async def generate_answer(question: str, chunks: list[RetrievedChunk]) -> AnswerResult:
    if not chunks:
        return AnswerResult(
            answer="I don't know based on the uploaded document.",
            sources=[],
        )

    if not settings.OPENAI_CONFIGURED:
        raise RuntimeError('OPENAI_API_KEY is not set. Add it to your .env to generate answers.')

    from openai import AsyncOpenAI

    context = '\n\n'.join(
        f'[Chunk {chunk.chunk_index}]\n{chunk.content}' for chunk in chunks
    )
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    response = await client.chat.completions.create(
        model=settings.OPENAI_CHAT_MODEL,
        temperature=0.1,
        messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {
                'role': 'user',
                'content': f'Context:\n{context}\n\nQuestion: {question}',
            },
        ],
    )
    answer = (response.choices[0].message.content or '').strip()
    return AnswerResult(answer=answer, sources=chunks)
