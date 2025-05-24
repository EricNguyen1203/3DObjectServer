from pydantic import BaseModel


class CreateImage360Request(BaseModel):
    title: str
    prompt: str