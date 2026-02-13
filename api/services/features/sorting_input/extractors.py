import re


def extract_sorter_id(message: str) -> str | None:
    patterns = [
        r"\bsorter\s*id\s*[:=]\s*([A-Za-z0-9-]+)",
        r"\bsorter\s*id\s+is\s+([A-Za-z0-9-]+)",
        r"\bset\s+sorter\s*id\s+to\s+([A-Za-z0-9-]+)",
        r"\bupdate\s+sorter\s*id\s+to\s+([A-Za-z0-9-]+)",
        r"\bchange\s+sorter\s*id\s+to\s+([A-Za-z0-9-]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, message, flags=re.IGNORECASE)
        if match:
            return match.group(match.lastindex)
    return None


def extract_tag_serial_no(message: str) -> str | None:
    patterns = [
        r"\btag\s+serial\s*(no|number)?\s*[:=]\s*([A-Za-z0-9-]+)",
        r"\btag\s+serial\s*(no|number)?\s+is\s+([A-Za-z0-9-]+)",
        r"\bset\s+tag\s+serial\s*(no|number)?\s+to\s+([A-Za-z0-9-]+)",
        r"\bupdate\s+tag\s+serial\s*(no|number)?\s+to\s+([A-Za-z0-9-]+)",
        r"\bchange\s+tag\s+serial\s*(no|number)?\s+to\s+([A-Za-z0-9-]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, message, flags=re.IGNORECASE)
        if match:
            return match.group(match.lastindex)
    return None
