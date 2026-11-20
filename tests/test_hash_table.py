import unittest

from src.hash_table import HashTable, LinearHashTable, horner_hash


class HashTableTest(unittest.TestCase):
    def test_put_get_remove_and_update(self):
        table = HashTable(11)
        table.put("a", 1)
        table.put("b", 2)
        self.assertEqual(table.get("a"), 1)
        table.put("a", 10)
        self.assertEqual(table.get("a"), 10)
        self.assertTrue(table.contains("b"))
        self.assertEqual(table.remove("b"), 2)
        self.assertFalse("b" in table)

    def test_missing_key(self):
        table = HashTable()
        with self.assertRaises(KeyError):
            table.get("missing")
        with self.assertRaises(KeyError):
            table.remove("missing")

    def test_resize_and_full_table(self):
        table = HashTable(11)
        for number in range(100):
            table.put(str(number), number)
        self.assertEqual(len(table), 100)
        for number in range(100):
            self.assertEqual(table.get(str(number)), number)

    def test_horner_wrap(self):
        self.assertEqual(horner_hash("abc", 11), horner_hash("abc", 11))
        self.assertTrue(0 <= horner_hash("abc", 11) < 11)


class LinearHashTableTest(unittest.TestCase):
    def test_linear_wrap_update_and_remove(self):
        table = LinearHashTable(11)
        for number in range(11):
            table.put(str(number), number)
        table.remove("5")
        table.put("5", 50)
        self.assertEqual(table.get("5"), 50)

    def test_full_table_resize(self):
        table = LinearHashTable(5)
        for number in range(20):
            table.put(str(number), number)
        self.assertEqual(len(table), 20)
        for number in range(20):
            self.assertEqual(table.get(str(number)), number)


if __name__ == "__main__":
    unittest.main()
