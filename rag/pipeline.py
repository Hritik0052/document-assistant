import logging
from pathlib import Path

from documents.models import Document, DocumentChunk
from rag.chunking import chunk_text, clean_text
from rag.embeddings import embed_texts
from rag.generate import generate_answer
from rag.loaders import load_file
from rag.retrieve import retrieve_chunks
from rag.schemas import AnswerResult

logger = logging.getLogger(__name__)


async def ingest_document(document_id: int) -> None:
    document = await Document.objects.aget(pk=document_id)
    document.status = Document.Status.PROCESSING
    document.error_message = ''
    await document.asave(update_fields=['status', 'error_message', 'updated_at'])
    logger.info('Ingest started for "%s" (%s)', document.title, document.original_name)

    try:
        extracted = await load_file(Path(document.file.path))
        text = clean_text(extracted.text)
        if not text:
            raise ValueError('No text could be extracted from this file.')

        chunks = chunk_text(text)
        if not chunks:
            raise ValueError('The document produced no chunks.')

        logger.info('Extracted %s chunks from "%s"', len(chunks), document.title)
        await DocumentChunk.objects.filter(document=document).adelete()
        await DocumentChunk.objects.abulk_create([
            DocumentChunk(
                document=document,
                chunk_index=chunk.index,
                content=chunk.content,
                token_count=chunk.token_count,
            )
            for chunk in chunks
        ])
        document.chunk_count = len(chunks)
        await document.asave(update_fields=['chunk_count', 'updated_at'])

        stored = [chunk async for chunk in DocumentChunk.objects.filter(document=document).order_by('chunk_index')]
        vectors = await embed_texts([chunk.content for chunk in stored])
        await DocumentChunk.objects.abulk_update(
            [
                DocumentChunk(pk=chunk.pk, embedding=vector)
                for chunk, vector in zip(stored, vectors)
            ],
            ['embedding'],
        )

        document.status = Document.Status.READY
        await document.asave(update_fields=['status', 'updated_at'])
        logger.info('Ingest finished for "%s"', document.title)
    except Exception as exc:
        logger.exception('Ingest error for document %s', document_id)
        document.status = Document.Status.FAILED
        document.error_message = str(exc)
        await document.asave(update_fields=['status', 'error_message', 'updated_at'])


async def answer_question(document: Document, question: str) -> AnswerResult:
    chunks = await retrieve_chunks(document, question)
    return await generate_answer(question, chunks)
