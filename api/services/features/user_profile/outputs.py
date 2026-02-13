from typing import Literal
from pydantic import BaseModel, Field


class ExtractionOutput(BaseModel):
    full_name: str | None = None
    email: str | None = None
    bio: str | None = None


class ValidationOutput(BaseModel):
    missing_fields: list[str] = Field(default_factory=list)
    is_complete: bool = False
    is_email_valid: bool = True


class ConfirmationOutput(BaseModel):
    action: Literal["request_more_info", "request_confirmation", "submit_request"]
    message: str
    awaiting_confirmation: bool


class AgenticOutput(BaseModel):
    extraction: ExtractionOutput
    validation: ValidationOutput
    confirmation: ConfirmationOutput
