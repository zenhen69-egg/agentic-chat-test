from api.schemas.sorting import SortingChatResponse, SortingInputUpdate
from api.services.features.sorting_input.extractors import (
    extract_sorter_id,
    extract_tag_serial_no,
)
from api.services.features.sorting_input.pipeline import run_agentic_pipeline
from api.services.features.sorting_input.session import ensure_session_id, get_session_state
from api.services.features.sorting_input.utils import (
    build_missing_message,
    clean_value,
    format_sorting_details,
    is_confirmation,
    merge_sorting,
    missing_fields,
)


async def process_sorting_input_chat(
    user_message: str,
    history: list,
    sorting: SortingInputUpdate,
    session_id: str | None = None,
) -> SortingChatResponse:
    session_id = ensure_session_id(session_id)
    session_state = get_session_state(session_id)
    session_history = list(session_state.get("history", []))
    session_sorting = session_state.get("sorting")
    awaiting_confirmation = bool(session_state.get("awaiting_confirmation"))

    if not isinstance(session_sorting, SortingInputUpdate):
        session_sorting = SortingInputUpdate()

    merged_base = merge_sorting(session_sorting, sorting)
    history_for_llm = session_history if session_history else list(history or [])

    agentic_output = await run_agentic_pipeline(user_message, history_for_llm, merged_base)
    if agentic_output:
        extracted = SortingInputUpdate(
            sorter_id=agentic_output.extraction.sorter_id,
            tag_serial_no=agentic_output.extraction.tag_serial_no,
        )
    else:
        extracted = SortingInputUpdate(
            sorter_id=extract_sorter_id(user_message),
            tag_serial_no=extract_tag_serial_no(user_message),
        )

    merged_sorting = merge_sorting(merged_base, extracted)
    updates = []
    if clean_value(extracted.sorter_id):
        updates.append("sorter_id")
    if clean_value(extracted.tag_serial_no):
        updates.append("tag_serial_no")
    missing = missing_fields(merged_sorting)
    is_complete = len(missing) == 0

    confirmed = is_confirmation(user_message)

    if agentic_output:
        action = agentic_output.confirmation.action
        message = agentic_output.confirmation.message
        awaiting_confirmation = agentic_output.confirmation.awaiting_confirmation
    else:
        if is_complete:
            action = "request_confirmation"
            summary = format_sorting_details(merged_sorting)
            message = f"{build_missing_message(missing, user_message, updates)}\n\n{summary}"
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
        summary = format_sorting_details(merged_sorting)
        message = f"{build_missing_message(missing, user_message, updates)}\n\n{summary}"
        awaiting_confirmation = True
    elif not is_complete and action == "submit_request":
        action = "request_more_info"
        message = build_missing_message(missing, user_message, updates)
        awaiting_confirmation = False

    merged_sorting.is_complete = is_complete

    updated_history = history_for_llm[:]
    updated_history.append({"role": "user", "content": user_message})
    updated_history.append({"role": "assistant", "content": message})
    session_state["history"] = updated_history
    session_state["sorting"] = merged_sorting
    session_state["awaiting_confirmation"] = awaiting_confirmation

    return SortingChatResponse(
        message=message,
        action=action,
        missing_fields=missing,
        sorting=merged_sorting,
        is_complete=is_complete,
        session_id=session_id,
    )
