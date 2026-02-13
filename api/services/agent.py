import json
import os
import re
import uuid
from typing import List
from openai import AsyncOpenAI
from dotenv import load_dotenv
from api.schemas.profile import UserProfileUpdate, AgentChatResponse

load_dotenv()

REQUIRED_FIELDS = ("full_name", "email", "bio")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
SESSION_MEMORY: dict[str, dict[str, object]] = {}


def _clean_value(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned if cleaned else None


def _is_valid_email(email: str | None) -> bool:
    """Validate email format."""
    if not email:
        return False
    # Basic email validation: must have @ and a domain with at least one dot
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return bool(re.match(pattern, email.strip()))


def _extract_email(message: str) -> str | None:
    patterns = [
        r"\bemail\s*[:=]\s*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})",
        r"\bemail\s+is\s+([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})",
        r"\bchange\s+(my\s+)?email\s+to\s+([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})",
        r"\bupdate\s+(my\s+)?email\s+to\s+([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})",
        r"\bset\s+(my\s+)?email\s+to\s+([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})",
    ]
    for pattern in patterns:
        match = re.search(pattern, message, flags=re.IGNORECASE)
        if match:
            return match.group(match.lastindex)

    match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", message)
    return match.group(0) if match else None


def _extract_name(message: str) -> str | None:
    patterns = [
        r"\bmy name is\s+([A-Za-z][A-Za-z\s'-]{1,60})",
        r"\bi am\s+([A-Za-z][A-Za-z\s'-]{1,60})",
        r"\bI'm\s+([A-Za-z][A-Za-z\s'-]{1,60})",
        r"\b(full name|name)\s+is\s+([A-Za-z][A-Za-z\s'-]{1,60})",
        r"\b(full name|name)\s*[:=]\s*([A-Za-z][A-Za-z\s'-]{1,60})",
        r"\bchange\s+(my\s+)?(full name|name)\s+to\s+([A-Za-z][A-Za-z\s'-]{1,60})",
        r"\bupdate\s+(my\s+)?(full name|name)\s+to\s+([A-Za-z][A-Za-z\s'-]{1,60})",
        r"\bset\s+(my\s+)?(full name|name)\s+to\s+([A-Za-z][A-Za-z\s'-]{1,60})",
    ]
    for pattern in patterns:
        match = re.search(pattern, message, flags=re.IGNORECASE)
        if match:
            value = match.group(match.lastindex).strip()
            return value
    return None


def _extract_bio(message: str) -> str | None:
    patterns = [
        r"\bbio\s*[:=]\s*(.+)$",
        r"\bbio\s+is\s+(.+)$",
        r"\bmy\s+bio\s+is\s+(.+)$",
        r"\bchange\s+(my\s+)?bio\s+to\s+(.+)$",
        r"\bupdate\s+(my\s+)?bio\s+to\s+(.+)$",
        r"\bset\s+(my\s+)?bio\s+to\s+(.+)$",
    ]
    for pattern in patterns:
        match = re.search(pattern, message, flags=re.IGNORECASE)
        if match:
            return match.group(match.lastindex).strip()
    return None


def _extract_json_object(content: str) -> dict | None:
    start = content.find("{")
    end = content.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(content[start : end + 1])
    except Exception:
        return None


async def _extract_with_llm(
    user_message: str,
    history: list,
    profile: UserProfileUpdate,
) -> UserProfileUpdate | None:
    if not OPENAI_API_KEY:
        return None

    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    system_prompt = (
        "Extract profile updates from the conversation. "
        "Return a JSON object with keys: full_name, email, bio. "
        "Use null for fields not provided."
    )
    profile_context = json.dumps(profile.model_dump())
    messages = [
        {"role": "system", "content": system_prompt},
        *history,
        {
            "role": "user",
            "content": f"Current profile: {profile_context}\nUser message: {user_message}",
        },
    ]

    try:
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0,
        )
        content = response.choices[0].message.content or ""
        data = _extract_json_object(content)
        if not data:
            return None
        return UserProfileUpdate(
            full_name=data.get("full_name"),
            email=data.get("email"),
            bio=data.get("bio"),
        )
    except Exception:
        return None


def _merge_profile(base: UserProfileUpdate, updates: UserProfileUpdate) -> UserProfileUpdate:
    return UserProfileUpdate(
        full_name=_clean_value(updates.full_name) or _clean_value(base.full_name),
        email=_clean_value(updates.email) or _clean_value(base.email),
        bio=_clean_value(updates.bio) or _clean_value(base.bio),
    )


def _missing_fields(profile: UserProfileUpdate) -> List[str]:
    missing = []
    for field_name in REQUIRED_FIELDS:
        if not _clean_value(getattr(profile, field_name)):
            missing.append(field_name)
    return missing


def _is_greeting(message: str) -> bool:
    message = message.strip().lower()
    return message in {"hi", "hello", "hey", "hiya", "yo"}


def _acknowledge_message(message: str) -> str:
    if _is_greeting(message):
        return "Hello!"
    return "Thanks for the note."


def _is_confirmation(message: str) -> bool:
    message = message.strip().lower()
    return message in {
        "yes",
        "yep",
        "yeah",
        "sure",
        "please submit",
        "submit",
        "submit now",
        "go ahead",
        "confirm",
    }


def _build_missing_message(
    missing: List[str],
    user_message: str,
    updates: List[str],
) -> str:
    update_note = ""
    if updates:
        update_note = f"I updated your {', '.join(updates)}. "

    if not missing:
        return (
            f"{update_note}Wonderful — everything looks complete. "
            "Would you like me to submit your request?"
        )

    friendly = ", ".join(missing)
    return (
        f"{_acknowledge_message(user_message)} "
        f"{update_note}I can help with your profile. "
        "May I have the following details: "
        f"{friendly}?"
    )


def _format_profile_details(profile: UserProfileUpdate) -> str:
    """Format profile in human-readable format."""
    details = []
    if _clean_value(profile.full_name):
        details.append(f"• Full Name: {profile.full_name}")
    if _clean_value(profile.email):
        details.append(f"• Email: {profile.email}")
    if _clean_value(profile.bio):
        details.append(f"• Bio: {profile.bio}")
    return "\n".join(details) if details else "No details yet."


def _ensure_session_id(session_id: str | None) -> str:
    if session_id:
        return session_id
    return str(uuid.uuid4())


def _get_session_state(session_id: str) -> dict[str, object]:
    if session_id not in SESSION_MEMORY:
        SESSION_MEMORY[session_id] = {
            "history": [],
            "profile": UserProfileUpdate(),
            "awaiting_confirmation": False,
        }
    return SESSION_MEMORY[session_id]


async def process_agent_chat(
    user_message: str,
    history: list,
    profile: UserProfileUpdate,
    session_id: str | None = None,
) -> AgentChatResponse:
    session_id = _ensure_session_id(session_id)
    session_state = _get_session_state(session_id)
    session_history = list(session_state.get("history", []))
    session_profile = session_state.get("profile")
    awaiting_confirmation = bool(session_state.get("awaiting_confirmation"))

    if not isinstance(session_profile, UserProfileUpdate):
        session_profile = UserProfileUpdate()

    merged_base = _merge_profile(session_profile, profile)
    history_for_llm = session_history if session_history else list(history or [])

    extracted = await _extract_with_llm(user_message, history_for_llm, merged_base)
    if extracted is None:
        extracted = UserProfileUpdate(
            full_name=_extract_name(user_message),
            email=_extract_email(user_message),
            bio=_extract_bio(user_message),
        )
    
    # Validate email format before merging
    validation_errors = []
    if _clean_value(extracted.email) and not _is_valid_email(extracted.email):
        validation_errors.append("email")
        extracted.email = None  # Don't save invalid email
    
    merged_profile = _merge_profile(merged_base, extracted)
    updates = []
    if _clean_value(extracted.full_name):
        updates.append("full name")
    if _clean_value(extracted.email):
        updates.append("email")
    if _clean_value(extracted.bio):
        updates.append("bio")
    missing = _missing_fields(merged_profile)
    is_complete = len(missing) == 0

    confirmed = _is_confirmation(user_message)
    
    # Build message with validation errors if any
    if validation_errors:
        error_msg = "I noticed an issue: the email format doesn't look valid. Please provide a valid email address (e.g., name@example.com)."
        action = "request_more_info"
        message = error_msg
        awaiting_confirmation = False
    elif is_complete and confirmed:
        action = "submit_request"
        message = "Great — I will submit your request now."
        awaiting_confirmation = False
    elif is_complete:
        action = "request_confirmation"
        profile_summary = _format_profile_details(merged_profile)
        message = f"{_build_missing_message(missing, user_message, updates)}\n\n{profile_summary}"
        awaiting_confirmation = True
    else:
        action = "request_more_info"
        message = _build_missing_message(missing, user_message, updates)
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
