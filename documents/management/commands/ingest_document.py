"""Run full ingest on an uploaded document (same path as upload background job)."""
import time

from django.core.management.base import BaseCommand

from documents.models import Document
from rag.ingest_sync import ingest_document_sync


class Command(BaseCommand):
    help = 'Ingest a document by id — extract, chunk, embed, mark ready/failed'

    def add_arguments(self, parser):
        parser.add_argument('document_id', type=int, help='Document primary key')

    def handle(self, *args, **options):
        document_id = options['document_id']
        try:
            doc = Document.objects.get(pk=document_id)
        except Document.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'Document {document_id} not found'))
            raise SystemExit(1)

        self.stdout.write(f'Ingesting id={doc.pk} title="{doc.title}" file={doc.original_name}')
        self.stdout.write(f'Current status: {doc.status}  chunks: {doc.chunk_count}')
        started = time.perf_counter()
        ingest_document_sync(document_id)
        doc.refresh_from_db()
        elapsed = time.perf_counter() - started
        self.stdout.write(f'Final status: {doc.status}  chunks: {doc.chunk_count}  ({elapsed:.1f}s)')
        if doc.status == Document.Status.FAILED:
            self.stderr.write(self.style.ERROR(f'Error: {doc.error_message}'))
            raise SystemExit(1)
        self.stdout.write(self.style.SUCCESS('Done.'))
