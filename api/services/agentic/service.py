from api.schemas.profile import AgentChatResponse, UserProfileUpdate
from api.services.agentic.extractors import extract_bio, extract_email, extract_name
from api.services.agentic.pipeline import run_agentic_pipeline
from api.services.agentic.session import ensure_session_id, get_session_state
from api.services.agentic.utils import (
    build_missing_message,
    clean_value,
    format_profile_details,
    is_confirmation,
    is_valid_email,
    merge_profile,
    missing_fields,
)


async def process_agent_chat(
    user_message: str,
    history: list,
    profile: UserProfileUpdate,
    session_id: str | None = None,
) -> AgentChatResponse:
    session_id = ensure_session_id(session_id)
    session_state = get_session_state(session_id)
    session_history = list(session_state.get("history", []))
    session_profile = session_state.get("profile")
    awaiting_confirmation = bool(session_state.get("awaiting_confirmation"))

    if not isinstance(session_profile, UserProfileUpdate):
        session_profile = UserProfileUpdate()

    merged_base = merge_profile(session_profile, profile)
    history_for_llm = session_history if session_history else list(history or [])

    agentic_output = await run_agentic_pipeline(user_message, history_for_llm, merged_base)
    if agentic_output:
        extracted = UserProfileUpdate(
            full_name=agentic_output.extraction.full_name,
            email=agentic_output.extraction.email,
            bio=agentic_output.extraction.bio,
        )
    else:
        extracted = UserProfileUpdate(
            full_name=extract_name(user_message),
            email=extract_email(user_message),
            bio=extract_bio(user_message),
        )

    validation_errors = []
    if clean_value(extracted.email) and not is_valid_email(extracted.email):
        validation_errors.append("email")
        extracted.email = None

    merged_profile = merge_profile(merged_base, extracted)
    updates = []
    if clean_value(extracted.full_name):
        updates.append("full_name")
    if clean_value(extracted.email):
        updates.append("email")
    if clean_value(extracted.bio):
        updates.append("bio")
    missing = missing_fields(merged_profile)
    is_complete = len(missing) == 0

    confirmed = is_confirmation(user_message)

    if validation_errors:
        message = (
            "Thanks! That email address doesn't look quite right. "
            "Could you share a valid one (for example, name@example.com)?"
        )
        action = "request_more_info"
        awaiting_confirmation = False
    else:
        if agentic_output:
            action = agentic_output.confirmation.action
            message = agentic_output.confirmation.message
            awaiting_confirmation = agentic_output.confirmation.awaiting_confirmation
        else:
            if is_complete:
                action = "request_confirmation"
                profile_summary = format_profile_details(merged_profile)
                message = (
                    f"{build_missing_message(missing, user_message, updates)}\n\n"
                    f"{profile_summary}"
                )
                awaiting_confirmation = True
            else:
                action = "request_more_info"
                message = build_missing_message(missing, user_message, updates)
                awaiting_confirmation = False

    if is_complete and confirmed:
        action = "submit_request"
        message = "Great — I will submit your request now."
        awaiting_confirmation = False
    elif is_complete and action == "request_more_info":
        action = "request_confirmation"
        profile_summary = format_profile_details(merged_profile)
        message = f"{build_missing_message(missing, user_message, updates)}\n\n{profile_summary}"
        awaiting_confirmation = True
    elif not is_complete and action == "submit_request":
        action = "request_more_info"
        message = build_missing_message(missing, user_message, updates)
        awaiting_confirmation = False

    merged_profile.is_complete = is_complete

    updated_history = history_for_llm[:]
    updated_history.append({"role": "user", "content": user_message})
    updated_history.append({"role": "assistant", "content": message})
    session_state["history"] = updated_history
    session_state["profile"] = merged_profile
    session_state["awaiting_confirmation"] = awaiting_confirmation

    return AgentChatResponse(
        message=message,
        action=action,
        missing_fields=missing,
        profile=merged_profile,
        is_complete=is_complete,
        session_id=session_id,
    )
