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

    def test_resize_can_be_disabled(self):
        table = HashTable(503, max_load=None)
        for number in range(100):
            table.put(str(number), number)
        self.assertEqual(table.size, 503)

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

    def test_wrap_from_last_slot_to_first_slot(self):
        table = LinearHashTable(5, max_load=None)
        table.put("b", 1)
        table.put("g", 2)
        table.put("l", 3)
        table.put("q", 4)
        table.put("v", 5)
        for number, key in enumerate(("b", "g", "l", "q", "v")):
            self.assertEqual(table.get(key), number + 1)

    def test_full_table_raises_runtime_error(self):
        table = LinearHashTable(5, max_load=None)
        for number in range(5):
            table.put(str(number), number)
        with self.assertRaises(RuntimeError):
            table.put("overflow", 100)

    def test_remove_reinsert_reuses_tombstone(self):
        table = LinearHashTable(5, max_load=None)
        table.put("a", 1)
        table.put("l", 2)
        self.assertEqual(table.remove("a"), 1)
        table.put("a", 3)
        self.assertEqual(table.get("a"), 3)


if __name__ == "__main__":
    unittest.main()
