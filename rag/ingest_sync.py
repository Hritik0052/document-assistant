"""Sync ingest for background threads — avoids async ORM deadlock in runserver."""
import asyncio
import logging
from pathlib import Path

from documents.models import Document, DocumentChunk
from rag.chunking import chunk_text, clean_text
from rag.embeddings import embed_texts
from rag.loaders import load_file

logger = logging.getLogger(__name__)


def ingest_document_sync(document_id: int) -> None:
    document = Document.objects.get(pk=document_id)
    document.status = Document.Status.PROCESSING
    document.error_message = ''
    document.save(update_fields=['status', 'error_message', 'updated_at'])
    logger.info('Ingest started for "%s" (%s)', document.title, document.original_name)

    try:
        extracted = asyncio.run(load_file(Path(document.file.path)))
        text = clean_text(extracted.text)
        if not text:
            raise ValueError('No text could be extracted from this file.')

        chunks = chunk_text(text)
        if not chunks:
            raise ValueError('The document produced no chunks.')

        logger.info('Extracted %s chunks from "%s"', len(chunks), document.title)
        DocumentChunk.objects.filter(document=document).delete()
        DocumentChunk.objects.bulk_create([
            DocumentChunk(
                document=document,
                chunk_index=chunk.index,
                content=chunk.content,
                token_count=chunk.token_count,
            )
            for chunk in chunks
        ])
        document.chunk_count = len(chunks)
        document.save(update_fields=['chunk_count', 'updated_at'])

        stored = list(DocumentChunk.objects.filter(document=document).order_by('chunk_index'))
        logger.info('Calling OpenRouter for %s chunk(s)...', len(stored))
        vectors = asyncio.run(embed_texts([chunk.content for chunk in stored]))

        for chunk, vector in zip(stored, vectors):
            chunk.embedding = vector
        DocumentChunk.objects.bulk_update(stored, ['embedding'])

        document.status = Document.Status.READY
        document.save(update_fields=['status', 'updated_at'])
        logger.info('Ingest finished for "%s" (%s chunks)', document.title, len(stored))
    except Exception as exc:
        logger.exception('Ingest error for document %s', document_id)
        document.status = Document.Status.FAILED
        document.error_message = str(exc)
        document.save(update_fields=['status', 'error_message', 'updated_at'])
