EXTRACTION_PROMPT = (
    "Extract profile updates from the conversation. "
    "Return JSON with keys: full_name, email, bio. "
    "Use null for fields not provided."
)

VALIDATION_PROMPT = (
    "Validate profile data. "
    "Return JSON with keys: missing_fields, is_complete, is_email_valid. "
    "missing_fields should include any missing among full_name, email, bio. "
    "is_email_valid should be true if email is missing or valid; false if invalid."
)

CONFIRMATION_PROMPT = (
    "Decide next action and craft a polite, conversational response. "
    "Return JSON with keys: action, message, awaiting_confirmation. "
    "When listing fields, use friendly labels: name, email address, short bio. "
    "If is_email_valid is false, action=request_more_info and ask for a valid email. "
    "If is_complete is true and user confirmed, action=submit_request. "
    "If is_complete is true and not confirmed, action=request_confirmation and ask to submit. "
    "If missing fields exist, action=request_more_info and list them. "
    "When is_complete is true, include a short human-readable profile summary."
)

MAIN_PROMPT = (
    "You are the main coordinator. "
    "Call tools in order: extract_profile_fields, validate_profile_state, "
    "craft_confirmation_message. "
    "Return JSON with keys: extraction, validation, confirmation."
)
