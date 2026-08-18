from django.test import SimpleTestCase

from rag.chunking import chunk_text, clean_text, estimate_tokens


class ChunkingTests(SimpleTestCase):
    def test_clean_text_collapses_whitespace(self):
        text = clean_text('Hello   world\n\n\nagain')
        self.assertEqual(text, 'Hello world\n\nagain')

    def test_chunk_text_creates_overlapping_windows(self):
        words = ' '.join(f'word{i}' for i in range(50))
        chunks = chunk_text(words, chunk_tokens=10, overlap_ratio=0.2)
        self.assertGreater(len(chunks), 1)
        self.assertEqual(chunks[0].index, 0)
        self.assertLessEqual(chunks[0].token_count, 10)

    def test_empty_text_returns_no_chunks(self):
        self.assertEqual(chunk_text(''), [])

    def test_estimate_tokens_counts_words(self):
        self.assertEqual(estimate_tokens('one two three'), 3)
