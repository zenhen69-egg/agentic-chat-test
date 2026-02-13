from typing import List
from api.schemas.sorting import SortingInputUpdate
from api.services.features.sorting_input.config import REQUIRED_FIELDS


FIELD_LABELS = {
    "sorter_id": "Sorter ID",
    "tag_serial_no": "Tag Serial No.",
}


def clean_value(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned if cleaned else None


def humanize_fields(fields: List[str]) -> List[str]:
    return [FIELD_LABELS.get(field, field.replace("_", " ")) for field in fields]


def merge_sorting(base: SortingInputUpdate, updates: SortingInputUpdate) -> SortingInputUpdate:
    return SortingInputUpdate(
        sorter_id=clean_value(updates.sorter_id) or clean_value(base.sorter_id),
        tag_serial_no=clean_value(updates.tag_serial_no) or clean_value(base.tag_serial_no),
    )


def missing_fields(sorting: SortingInputUpdate) -> List[str]:
    missing = []
    for field_name in REQUIRED_FIELDS:
        if not clean_value(getattr(sorting, field_name)):
            missing.append(field_name)
    return missing


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
        f"{update_note}I can help with your sorting input. "
        "May I have the following details: "
        f"{friendly}?"
    )


def format_sorting_details(sorting: SortingInputUpdate) -> str:
    details = []
    if clean_value(sorting.sorter_id):
        details.append(f"• Sorter ID: {sorting.sorter_id}")
    if clean_value(sorting.tag_serial_no):
        details.append(f"• Tag Serial No.: {sorting.tag_serial_no}")
    return "\n".join(details) if details else "No details yet."
