import re


def is_url(text: str) -> bool:
    """Return True if the given string looks like a URL."""
    pattern = re.compile(
        r'^(https?://)'
        r'([a-zA-Z0-9\-\.]+)'
        r'(\.[a-zA-Z]{2,})'
        r'(/.*)?$'
    )
    return bool(pattern.match(text.strip()))


def success_response(data: dict, status: int = 200):
    """Wrap data in a standard success envelope."""
    return {"success": True, "data": data}, status


def error_response(message: str, status: int = 400):
    """Wrap an error message in a standard error envelope."""
    return {"success": False, "error": message}, status
