from agents import Agent, AgentOutputSchema
from api.services.features.sorting_input.config import MODEL_SETTINGS, OPENAI_MODEL
from api.services.features.sorting_input.outputs import (
    ConfirmationOutput,
    ExtractionOutput,
    ValidationOutput,
)
from api.services.features.sorting_input.prompts import (
    CONFIRMATION_PROMPT,
    EXTRACTION_PROMPT,
    VALIDATION_PROMPT,
)


extraction_agent = Agent(
    name="SortingExtractionAgent",
    instructions=EXTRACTION_PROMPT,
    model=OPENAI_MODEL,
    model_settings=MODEL_SETTINGS,
    output_type=AgentOutputSchema(ExtractionOutput, strict_json_schema=False),
)


validation_agent = Agent(
    name="SortingValidationAgent",
    instructions=VALIDATION_PROMPT,
    model=OPENAI_MODEL,
    model_settings=MODEL_SETTINGS,
    output_type=AgentOutputSchema(ValidationOutput, strict_json_schema=False),
)


confirmation_agent = Agent(
    name="SortingConfirmationAgent",
    instructions=CONFIRMATION_PROMPT,
    model=OPENAI_MODEL,
    model_settings=MODEL_SETTINGS,
    output_type=AgentOutputSchema(ConfirmationOutput, strict_json_schema=False),
)
