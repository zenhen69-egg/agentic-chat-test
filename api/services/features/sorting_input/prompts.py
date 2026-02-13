EXTRACTION_PROMPT = (
    "Extract sorting input updates from the conversation. "
    "Return JSON with keys: sorter_id, tag_serial_no. "
    "Use null for fields not provided."
)

VALIDATION_PROMPT = (
    "Validate sorting input data. "
    "Return JSON with keys: missing_fields, is_complete. "
    "missing_fields should include any missing among sorter_id, tag_serial_no."
)

CONFIRMATION_PROMPT = (
    "Decide next action and craft a polite, conversational response. "
    "Return JSON with keys: action, message, awaiting_confirmation. "
    "When listing fields, use friendly labels: Sorter ID, Tag Serial No. "
    "If is_complete is true and user confirmed, action=submit_request. "
    "If is_complete is true and not confirmed, action=request_confirmation and ask to submit. "
    "If missing fields exist, action=request_more_info and list them. "
    "When is_complete is true, include a short human-readable summary."
)

MAIN_PROMPT = (
    "You are the main coordinator. "
    "Call tools in order: extract_sorting_fields, validate_sorting_state, "
    "craft_confirmation_message. "
    "Return JSON with keys: extraction, validation, confirmation."
)
