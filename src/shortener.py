"""Base62 helpers and URL shortener implementation."""

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
from urllib.parse import urlparse

try:
    from .hash_table import HashTable, LinearHashTable
except ImportError:
    from hash_table import HashTable, LinearHashTable


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
        position = ALPHABET.find(char)
        if position < 0:
            raise ValueError("code contains a character outside the Base62 alphabet")
        value = value * len(ALPHABET) + position
    return value


def validate_url(url: str) -> str:
    if not isinstance(url, str):
        raise TypeError("url must be a string")
    if not url:
        raise ValueError("url must not be empty")
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("url must be a valid HTTP or HTTPS URL")
    if any(char.isspace() for char in url):
        raise ValueError("url must not contain whitespace")
    try:
        hostname = parsed.hostname
    except ValueError as exc:
        raise ValueError("url must be a valid HTTP or HTTPS URL") from exc
    if not hostname:
        raise ValueError("url must be a valid HTTP or HTTPS URL")
    return url


class URLShortener:
    """Stores URLs and creates stable Base62 codes."""

    def __init__(self, table=None, table_type="chaining"):
        if table is not None:
            code_table = table
        elif table_type == "chaining":
            code_table = HashTable()
        elif table_type == "linear":
            code_table = LinearHashTable()
        else:
            raise ValueError("table_type must be 'chaining' or 'linear'")
        self.url_to_code = HashTable()
        self.code_to_url = code_table
        self.next_id = 1

    def shorten(self, url: str) -> str:
        url = validate_url(url)
        if url in self.url_to_code:
            return self.url_to_code.get(url)
        code = encode(self.next_id)
        self.next_id += 1
        self.url_to_code.put(url, code)
        self.code_to_url.put(code, url)
        return code

    def expand(self, code: str) -> str:
        if not isinstance(code, str):
            raise TypeError("code must be a string")
        return self.code_to_url.get(code)
