import unittest

from src.base62 import decode, encode


class Base62Test(unittest.TestCase):
    def test_encode_zero(self):
        self.assertEqual(encode(0), "0")

    def test_known_values(self):
        cases = {
            0: "0",
            1: "1",
            9: "9",
            10: "a",
            35: "z",
            36: "A",
            61: "Z",
            62: "10",
            3844: "100",
        }
        for number, code in cases.items():
            self.assertEqual(encode(number), code)

    def test_decode_known_values(self):
        cases = {
            "0": 0,
            "1": 1,
            "9": 9,
            "a": 10,
            "z": 35,
            "A": 36,
            "Z": 61,
            "10": 62,
            "100": 3844,
        }
        for code, number in cases.items():
            self.assertEqual(decode(code), number)

    def test_round_trip(self):
        for number in range(10000):
            self.assertEqual(decode(encode(number)), number)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            encode(-1)
        with self.assertRaises(TypeError):
            encode(1.5)
        with self.assertRaises(ValueError):
            decode("")
        with self.assertRaises(ValueError):
            decode("+10")
        with self.assertRaises(TypeError):
            decode(10)


if __name__ == "__main__":
    unittest.main()
