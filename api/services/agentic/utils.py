import re
from typing import List
from api.schemas.profile import UserProfileUpdate
from api.services.agentic.config import REQUIRED_FIELDS


def clean_value(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned if cleaned else None


def is_valid_email(email: str | None) -> bool:
    if not email:
        return False
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return bool(re.match(pattern, email.strip()))


def merge_profile(base: UserProfileUpdate, updates: UserProfileUpdate) -> UserProfileUpdate:
    return UserProfileUpdate(
        full_name=clean_value(updates.full_name) or clean_value(base.full_name),
        email=clean_value(updates.email) or clean_value(base.email),
        bio=clean_value(updates.bio) or clean_value(base.bio),
    )


def missing_fields(profile: UserProfileUpdate) -> List[str]:
    missing = []
    for field_name in REQUIRED_FIELDS:
        if not clean_value(getattr(profile, field_name)):
            missing.append(field_name)
    return missing


FIELD_LABELS = {
    "full_name": "name",
    "email": "email address",
    "bio": "short bio",
}


def humanize_fields(fields: List[str]) -> List[str]:
    return [FIELD_LABELS.get(field, field.replace("_", " ")) for field in fields]


def is_greeting(message: str) -> bool:
    message = message.strip().lower()
    return message in {"hi", "hello", "hey", "hiya", "yo"}


def acknowledge_message(message: str) -> str:
    if is_greeting(message):
        return "Hello!"
    return "Thanks for the note."


def is_confirmation(message: str) -> bool:
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


def build_missing_message(
    missing: List[str],
    user_message: str,
    updates: List[str],
) -> str:
    update_note = ""
    if updates:
        update_note = f"I updated your {', '.join(humanize_fields(updates))}. "

    if not missing:
        return (
            f"{update_note}Wonderful — everything looks complete. "
            "Would you like me to submit your request?"
        )

    friendly = ", ".join(humanize_fields(missing))
    return (
        f"{acknowledge_message(user_message)} "
        f"{update_note}I can help with your profile. "
        "May I have the following details: "
        f"{friendly}?"
    )


def format_profile_details(profile: UserProfileUpdate) -> str:
    details = []
    if clean_value(profile.full_name):
        details.append(f"• Name: {profile.full_name}")
    if clean_value(profile.email):
        details.append(f"• Email address: {profile.email}")
    if clean_value(profile.bio):
        details.append(f"• Short bio: {profile.bio}")
    return "\n".join(details) if details else "No details yet."
