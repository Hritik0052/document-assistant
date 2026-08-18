from pathlib import Path

from rag.loaders.base import BaseLoader
from rag.loaders.docx import DocxLoader
from rag.loaders.pdf import PdfLoader
from rag.loaders.txt import TxtLoader
from rag.schemas import ExtractedDocument

_LOADERS: dict[str, BaseLoader] = {
    loader.suffix: loader
    for loader in (PdfLoader(), TxtLoader(), DocxLoader())
}


async def load_file(path: Path) -> ExtractedDocument:
    suffix = path.suffix.lower()
    loader = _LOADERS.get(suffix)
    if loader is None:
        raise ValueError(f'No loader registered for {suffix} files.')
    return await loader.load(path)
