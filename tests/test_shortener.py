import unittest

from src.shortener import decode, encode


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


if __name__ == "__main__":
    unittest.main()
