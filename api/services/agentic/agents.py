from agents import Agent, AgentOutputSchema
from api.services.agentic.config import MODEL_SETTINGS, OPENAI_MODEL
from api.services.agentic.outputs import ConfirmationOutput, ExtractionOutput, ValidationOutput
from api.services.agentic.prompts import CONFIRMATION_PROMPT, EXTRACTION_PROMPT, VALIDATION_PROMPT


extraction_agent = Agent(
    name="ProfileExtractionAgent",
    instructions=EXTRACTION_PROMPT,
    model=OPENAI_MODEL,
    model_settings=MODEL_SETTINGS,
    output_type=AgentOutputSchema(ExtractionOutput, strict_json_schema=False),
)


validation_agent = Agent(
    name="ValidationAgent",
    instructions=VALIDATION_PROMPT,
    model=OPENAI_MODEL,
    model_settings=MODEL_SETTINGS,
    output_type=AgentOutputSchema(ValidationOutput, strict_json_schema=False),
)


confirmation_agent = Agent(
    name="ConfirmationAgent",
    instructions=CONFIRMATION_PROMPT,
    model=OPENAI_MODEL,
    model_settings=MODEL_SETTINGS,
    output_type=AgentOutputSchema(ConfirmationOutput, strict_json_schema=False),
)
