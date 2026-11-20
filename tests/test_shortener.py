import unittest

from src.shortener import URLShortener, decode, encode, validate_url
from src.hash_table import LinearHashTable


class Base62Test(unittest.TestCase):
    def test_encode_zero(self):
        self.assertEqual(encode(0), "0")

    def test_known_values_and_round_trip(self):
        values = {
            1: "1",
            10: "a",
            61: "Z",
            62: "10",
            3844: "100",
        }
        for number, code in values.items():
            self.assertEqual(encode(number), code)
            self.assertEqual(decode(code), number)

    def test_round_trip_range(self):
        for number in range(10000):
            self.assertEqual(decode(encode(number)), number)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            encode(-1)
        with self.assertRaises(ValueError):
            decode("")
        with self.assertRaises(ValueError):
            decode("+10")
        with self.assertRaises(TypeError):
            encode("10")

    def test_shortener_is_stable(self):
        shortener = URLShortener()
        first = shortener.shorten("https://example.com/a")
        second = shortener.shorten("https://example.com/a")
        self.assertEqual(first, "1")
        self.assertEqual(second, "1")
        self.assertEqual(shortener.expand(first), "https://example.com/a")
        with self.assertRaises(KeyError):
            shortener.expand("missing")

    def test_invalid_urls(self):
        shortener = URLShortener()
        for url in ("", "example.com", "ftp://example.com"):
            with self.assertRaises(ValueError):
                validate_url(url)
                shortener.shorten(url)

    def test_linear_table_choice(self):
        shortener = URLShortener(table_type="linear")
        self.assertIsInstance(shortener.code_to_url, LinearHashTable)

    def test_linear_shortener_matches_chaining_behavior(self):
        shortener = URLShortener(table_type="linear")
        first = shortener.shorten("https://example.com/linear")
        second = shortener.shorten("https://example.com/linear")
        self.assertEqual(first, second)
        self.assertEqual(shortener.expand(first), "https://example.com/linear")


if __name__ == "__main__":
    unittest.main()
