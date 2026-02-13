import re


def extract_email(message: str) -> str | None:
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


def extract_name(message: str) -> str | None:
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


def extract_bio(message: str) -> str | None:
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
