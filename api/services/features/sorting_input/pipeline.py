import json
from agents import Agent, AgentOutputSchema, Runner
from api.schemas.sorting import SortingInputUpdate
from api.services.features.sorting_input.config import MODEL_SETTINGS, OPENAI_API_KEY, OPENAI_MODEL
from api.services.features.sorting_input.outputs import AgenticOutput
from api.services.features.sorting_input.prompts import MAIN_PROMPT
from api.services.features.sorting_input.tools import (
    craft_confirmation_message,
    extract_sorting_fields,
    validate_sorting_state,
)


main_agent = Agent(
    name="MainSortingAgent",
    instructions=MAIN_PROMPT,
    model=OPENAI_MODEL,
    model_settings=MODEL_SETTINGS,
    tools=[
        extract_sorting_fields,
        validate_sorting_state,
        craft_confirmation_message,
    ],
    output_type=AgentOutputSchema(AgenticOutput, strict_json_schema=False),
)


async def run_agentic_pipeline(
    user_message: str,
    history: list,
    sorting: SortingInputUpdate,
) -> AgenticOutput | None:
    if not OPENAI_API_KEY:
        return None

    input_text = json.dumps(
        {
            "user_message": user_message,
            "history": history,
            "sorting": sorting.model_dump(),
        },
        ensure_ascii=True,
    )
    try:
        result = await Runner.run(main_agent, input=input_text)
        return AgenticOutput.model_validate(result.final_output)
    except Exception:
        return None
