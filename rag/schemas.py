from pydantic import BaseModel, Field


class ExtractedDocument(BaseModel):
    text: str
    source: str = ''
    extra: dict = Field(default_factory=dict)


class Chunk(BaseModel):
    index: int
    content: str
    token_count: int


class RetrievedChunk(BaseModel):
    chunk_index: int
    content: str
    similarity: float


class AnswerResult(BaseModel):
    answer: str
    sources: list[RetrievedChunk] = Field(default_factory=list)
