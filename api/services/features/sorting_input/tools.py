import json
from agents import Runner, function_tool
from api.services.features.sorting_input.agents import (
    confirmation_agent,
    extraction_agent,
    validation_agent,
)
from api.services.features.sorting_input.outputs import (
    ConfirmationOutput,
    ExtractionOutput,
    ValidationOutput,
)


@function_tool(strict_mode=False)
async def extract_sorting_fields(
    user_message: str,
    history: list,
    sorting: dict,
) -> ExtractionOutput:
    """Extract sorting input fields from the conversation."""
    input_text = json.dumps(
        {
            "user_message": user_message,
            "history": history,
            "sorting": sorting,
        },
        ensure_ascii=True,
    )
    result = await Runner.run(extraction_agent, input=input_text)
    return ExtractionOutput.model_validate(result.final_output)


@function_tool(strict_mode=False)
async def validate_sorting_state(sorting: dict) -> ValidationOutput:
    """Validate sorting input completeness."""
    input_text = json.dumps({"sorting": sorting}, ensure_ascii=True)
    result = await Runner.run(validation_agent, input=input_text)
    return ValidationOutput.model_validate(result.final_output)


@function_tool(strict_mode=False)
async def craft_confirmation_message(
    user_message: str,
    updates: list[str],
    sorting: dict,
    missing_fields: list[str],
    is_complete: bool,
) -> ConfirmationOutput:
    """Create the response message and next action."""
    input_text = json.dumps(
        {
            "user_message": user_message,
            "updates": updates,
            "sorting": sorting,
            "missing_fields": missing_fields,
            "is_complete": is_complete,
        },
        ensure_ascii=True,
    )
    result = await Runner.run(confirmation_agent, input=input_text)
    return ConfirmationOutput.model_validate(result.final_output)
