import json
from agents import Runner, function_tool
from api.services.agentic.agents import confirmation_agent, extraction_agent, validation_agent
from api.services.agentic.outputs import ConfirmationOutput, ExtractionOutput, ValidationOutput


@function_tool(strict_mode=False)
async def extract_profile_fields(
    user_message: str,
    history: list,
    profile: dict,
) -> ExtractionOutput:
    """Extract profile fields from the conversation."""
    input_text = json.dumps(
        {
            "user_message": user_message,
            "history": history,
            "profile": profile,
        },
        ensure_ascii=True,
    )
    result = await Runner.run(extraction_agent, input=input_text)
    return ExtractionOutput.model_validate(result.final_output)


@function_tool(strict_mode=False)
async def validate_profile_state(profile: dict) -> ValidationOutput:
    """Validate profile completeness and email format."""
    input_text = json.dumps({"profile": profile}, ensure_ascii=True)
    result = await Runner.run(validation_agent, input=input_text)
    return ValidationOutput.model_validate(result.final_output)


@function_tool(strict_mode=False)
async def craft_confirmation_message(
    user_message: str,
    updates: list[str],
    profile: dict,
    missing_fields: list[str],
    is_complete: bool,
    is_email_valid: bool,
) -> ConfirmationOutput:
    """Create the response message and next action."""
    input_text = json.dumps(
        {
            "user_message": user_message,
            "updates": updates,
            "profile": profile,
            "missing_fields": missing_fields,
            "is_complete": is_complete,
            "is_email_valid": is_email_valid,
        },
        ensure_ascii=True,
    )
    result = await Runner.run(confirmation_agent, input=input_text)
    return ConfirmationOutput.model_validate(result.final_output)
