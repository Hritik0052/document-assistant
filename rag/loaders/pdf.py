from pathlib import Path

from asgiref.sync import sync_to_async
from pypdf import PdfReader

from rag.loaders.base import BaseLoader
from rag.schemas import ExtractedDocument


class PdfLoader(BaseLoader):
    suffix = '.pdf'

    async def load(self, path: Path) -> ExtractedDocument:
        return await sync_to_async(self._load_sync)(path)

    def _load_sync(self, path: Path) -> ExtractedDocument:
        reader = PdfReader(str(path))
        pages = []
        for index, page in enumerate(reader.pages, start=1):
            content = page.extract_text() or ''
            pages.append(content)
        text = '\n\n'.join(pages)
        return ExtractedDocument(
            text=text,
            source=path.name,
            extra={'loader': 'pdf', 'pages': len(pages)},
        )
