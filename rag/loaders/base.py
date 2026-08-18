from abc import ABC, abstractmethod
from pathlib import Path

from rag.schemas import ExtractedDocument


class BaseLoader(ABC):
    suffix: str

    @abstractmethod
    async def load(self, path: Path) -> ExtractedDocument:
        raise NotImplementedError
