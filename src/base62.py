"""Base62 encoding and decoding helpers."""

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def encode(n: int) -> str:
    """Encode a non-negative integer into a Base62 string."""
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("n must be an integer")
    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0:
        return "0"

    chars = []
    while n:
        n, remainder = divmod(n, len(ALPHABET))
        chars.append(ALPHABET[remainder])
    return "".join(reversed(chars))


def decode(s: str) -> int:
    """Decode a Base62 string into a non-negative integer."""
    if not isinstance(s, str):
        raise TypeError("s must be a string")
    if not s:
        raise ValueError("s must not be empty")

    value = 0
    for char in s:
        position = ALPHABET.find(char)
        if position < 0:
            raise ValueError("s contains a character outside the Base62 alphabet")
        value = value * len(ALPHABET) + position
    return value
