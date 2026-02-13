import json
from agents import Agent, AgentOutputSchema, Runner
from api.schemas.profile import UserProfileUpdate
from api.services.features.user_profile.config import MODEL_SETTINGS, OPENAI_API_KEY, OPENAI_MODEL
from api.services.features.user_profile.outputs import AgenticOutput
from api.services.features.user_profile.prompts import MAIN_PROMPT
from api.services.features.user_profile.tools import (
    craft_confirmation_message,
    extract_profile_fields,
    validate_profile_state,
)


main_agent = Agent(
    name="MainProfileAgent",
    instructions=MAIN_PROMPT,
    model=OPENAI_MODEL,
    model_settings=MODEL_SETTINGS,
    tools=[
        extract_profile_fields,
        validate_profile_state,
        craft_confirmation_message,
    ],
    output_type=AgentOutputSchema(AgenticOutput, strict_json_schema=False),
)


async def run_agentic_pipeline(
    user_message: str,
    history: list,
    profile: UserProfileUpdate,
) -> AgenticOutput | None:
    if not OPENAI_API_KEY:
        return None

    input_text = json.dumps(
        {
            "user_message": user_message,
            "history": history,
            "profile": profile.model_dump(),
        },
        ensure_ascii=True,
    )
    try:
        result = await Runner.run(main_agent, input=input_text)
        return AgenticOutput.model_validate(result.final_output)
    except Exception:
        return None
