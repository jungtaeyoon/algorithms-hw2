"""Base62 helpers and URL shortener implementation."""

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
_VALUE = {char: index for index, char in enumerate(ALPHABET)}


def encode(number: int) -> str:
    """Encode a non-negative integer as a Base62 string."""
    if isinstance(number, bool) or not isinstance(number, int):
        raise TypeError("number must be an integer")
    if number < 0:
        raise ValueError("number must be non-negative")
    if number == 0:
        return "0"

    chars = []
    while number:
        number, remainder = divmod(number, len(ALPHABET))
        chars.append(ALPHABET[remainder])
    return "".join(reversed(chars))


def decode(code: str) -> int:
    """Decode a Base62 string into a non-negative integer."""
    if not isinstance(code, str):
        raise TypeError("code must be a string")
    if not code:
        raise ValueError("code must not be empty")

    value = 0
    for char in code:
        if char not in _VALUE:
            raise ValueError("code contains a character outside the Base62 alphabet")
        value = value * len(ALPHABET) + _VALUE[char]
    return value
