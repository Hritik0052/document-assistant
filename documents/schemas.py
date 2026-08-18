from pydantic import BaseModel, Field


class AskSchema(BaseModel):
    question: str = Field(min_length=3, max_length=2000)

    @property
    def cleaned_question(self) -> str:
        return ' '.join(self.question.split())
