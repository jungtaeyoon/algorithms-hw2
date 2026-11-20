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

    def test_empty_table(self):
        table = HashTable()
        self.assertEqual(len(table), 0)
        self.assertFalse("missing" in table)
        with self.assertRaises(KeyError):
            table.get("missing")

    def test_resize_can_be_disabled_with_max_load_none(self):
        table = HashTable(4093, max_load=None)
        for number in range(500):
            table.put(f"key-{number}", number)
        self.assertEqual(table.size, 4093)
        self.assertEqual(len(table), 500)

    def test_colliding_keys_share_a_chain(self):
        table = HashTable(11)
        self.assertEqual(horner_hash("a", 11), horner_hash("l", 11))
        table.put("a", 1)
        table.put("l", 2)
        self.assertEqual(table.get("a"), 1)
        self.assertEqual(table.get("l"), 2)
        self.assertEqual(table.remove("a"), 1)
        self.assertEqual(table.get("l"), 2)

    def test_remove_reinsert_and_update(self):
        table = HashTable(11)
        table.put("key", 1)
        table.put("key", 2)
        self.assertEqual(table.get("key"), 2)
        self.assertEqual(table.remove("key"), 2)
        with self.assertRaises(KeyError):
            table.get("key")
        table.put("key", 3)
        self.assertEqual(table.get("key"), 3)
        self.assertEqual(len(table), 1)

    def test_lookup_and_remove_missing_key(self):
        table = HashTable(11)
        with self.assertRaises(KeyError):
            table.get("missing")
        with self.assertRaises(KeyError):
            table.remove("missing")
        self.assertFalse(table.contains("missing"))

    def test_resize_preserves_every_key(self):
        table = HashTable(11)
        keys = [f"url-{number}" for number in range(30)]
        for number, key in enumerate(keys):
            table.put(key, number)
        self.assertGreater(table.size, 11)
        for number, key in enumerate(keys):
            self.assertEqual(table.get(key), number)
        self.assertEqual(len(table), len(keys))

    def test_non_string_keys_are_rejected(self):
        table = HashTable()
        for key in (None, 10, 1.5, True, ["key"]):
            with self.subTest(key=key):
                with self.assertRaises(TypeError):
                    table.put(key, "value")

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
