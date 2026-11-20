import unittest

from src.hash_table import LinearHashTable
from src.shortener import URLShortener, decode, encode, validate_url


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
            with self.subTest(url=url):
                with self.assertRaises(ValueError):
                    validate_url(url)
                    shortener.shorten(url)

    def test_url_and_code_types_are_rejected(self):
        shortener = URLShortener()
        for url in (None, 10, 1.5, True, ["https://example.com"]):
            with self.subTest(url=url):
                with self.assertRaises(TypeError):
                    shortener.shorten(url)
        for code in (None, 10, 1.5, True, ["1"]):
            with self.subTest(code=code):
                with self.assertRaises(TypeError):
                    shortener.expand(code)

    def test_hosts_and_supported_schemes(self):
        shortener = URLShortener()
        invalid_urls = (
            "http://",
            "https://",
            "ftp://example.com",
            "mailto:user@example.com",
        )
        for url in invalid_urls:
            with self.subTest(url=url):
                with self.assertRaises(ValueError):
                    shortener.shorten(url)

    def test_repeated_url_returns_same_code(self):
        shortener = URLShortener()
        url = "https://example.com/repeat"
        code = shortener.shorten(url)
        self.assertEqual(shortener.shorten(url), code)
        self.assertEqual(shortener.expand(code), url)

    def test_different_urls_return_different_codes(self):
        shortener = URLShortener()
        first = "https://example.com/first"
        second = "https://example.com/second"
        first_code = shortener.shorten(first)
        second_code = shortener.shorten(second)
        self.assertNotEqual(first_code, second_code)
        self.assertEqual(shortener.expand(first_code), first)
        self.assertEqual(shortener.expand(second_code), second)

    def test_missing_code_and_empty_code(self):
        shortener = URLShortener()
        for code in ("missing", ""):
            with self.subTest(code=code):
                with self.assertRaises(KeyError):
                    shortener.expand(code)

    def test_table_type_selects_supported_hash_table(self):
        chaining = URLShortener(table_type="chaining")
        linear = URLShortener(table_type="linear")
        self.assertNotIsInstance(chaining.code_to_url, LinearHashTable)
        self.assertIsInstance(linear.code_to_url, LinearHashTable)
        with self.assertRaises(ValueError):
            URLShortener(table_type="unknown")


if __name__ == "__main__":
    unittest.main()
