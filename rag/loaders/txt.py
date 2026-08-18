from pathlib import Path

from rag.loaders.base import BaseLoader
from rag.schemas import ExtractedDocument


class TxtLoader(BaseLoader):
    suffix = '.txt'

    async def load(self, path: Path) -> ExtractedDocument:
        text = path.read_text(encoding='utf-8', errors='ignore')
        return ExtractedDocument(text=text, source=path.name, extra={'loader': 'txt'})
