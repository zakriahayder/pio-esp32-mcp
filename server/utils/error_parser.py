import re
from server.schemas import ParsedError

# Example error message:
# src/main.cpp:5:5: error: 'foo' was not declared in this scope
_ERROR_RE = re.compile(r"^(.+?):(\d+):\d+:\s+error:\s+(.+)$", re.MULTILINE)


def parse_errors(stderr: str) -> list[ParsedError]:
    """Converts raw compiler error text and converts it into structured error
    information for the LLM

    Args:
        stderr (str): raw compiler error.

    Returns:
        list[ParsedError]
    """
    return [
        {"file": e.group(1), "line": int(e.group(2)), "message": e.group(3)}
        for e in _ERROR_RE.finditer(stderr)
    ]
