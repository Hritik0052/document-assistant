"""Django management command — tests the same rag.embeddings code path as upload."""
import asyncio
import time

from django.conf import settings
from django.core.management.base import BaseCommand

from rag.embeddings import embed_texts


class Command(BaseCommand):
    help = 'Smoke-test OpenRouter embeddings via rag.embeddings.embed_texts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--text',
            nargs='+',
            default=['This is a small test sentence for RAG embeddings.'],
            help='Text(s) to embed',
        )

    def handle(self, *args, **options):
        texts = options['text']
        self.stdout.write('=== Django rag.embeddings test ===')
        self.stdout.write(f'model: {settings.OPENROUTER_EMBEDDING_MODEL}')
        self.stdout.write(f'llm_configured: {settings.LLM_CONFIGURED}')
        self.stdout.write(f'inputs: {len(texts)}')

        started = time.perf_counter()
        try:
            vectors = asyncio.run(embed_texts(texts))
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f'FAILED: {type(exc).__name__}: {exc}'))
            raise SystemExit(1) from exc

        elapsed = time.perf_counter() - started
        for index, vector in enumerate(vectors):
            self.stdout.write(
                f'  [{index}] dim={len(vector)} '
                f'sample=[{vector[0]:.6f}, {vector[1]:.6f}, {vector[2]:.6f}, ...]'
            )
        self.stdout.write(self.style.SUCCESS(
            f'SUCCESS: got {len(vectors)} embedding(s) in {elapsed:.2f}s'
        ))
