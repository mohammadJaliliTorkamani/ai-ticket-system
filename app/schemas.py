from typing import Literal

from pydantic import BaseModel, Field, SecretStr, field_validator


class RespondRequest(BaseModel):
    api_key: SecretStr = Field(min_length=20, max_length=512)
    message: str = Field(min_length=1, max_length=10_000)
    model: str = Field(min_length=1, max_length=80)

    @field_validator("message")
    @classmethod
    def clean_message(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Message cannot be empty")
        if "\x00" in value:
            raise ValueError("Null bytes are not allowed")
        return value


class UsageOut(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


class TranscriptEntry(BaseModel):
    direction: Literal["browser_to_ticketifier", "ticketifier_to_openai", "openai_to_ticketifier", "ticketifier_to_browser"]
    method: str | None = None
    path: str | None = None
    status: int | None = None
    headers: dict[str, str] = Field(default_factory=dict)
    body: dict | str


class RespondResponse(BaseModel):
    status: Literal["completed"] = "completed"
    request_id: str
    provider_request_id: str | None = None
    model: str
    latency_ms: int
    output: str
    usage: UsageOut
    transcript: list[TranscriptEntry]
