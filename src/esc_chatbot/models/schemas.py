from pydantic import BaseModel, Field


class Message(BaseModel):
    text: str = Field(..., max_length=200)


class FeedbackPayload(BaseModel):
    text: str = Field(..., max_length=300)
    intent: str = Field(..., max_length=50)
    positive: bool = Field(...)
    comment: str = Field("", max_length=500)
