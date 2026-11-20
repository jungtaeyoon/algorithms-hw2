"""Hash-table implementations without Python hash tables or built-in hash."""


def horner_hash(key: str, size: int) -> int:
    if not isinstance(key, str):
        raise TypeError("key must be a string")
    value = 0
    for char in key:
        value = (value * 31 + ord(char)) % size
    return value


def next_prime(number: int) -> int:
    number = max(number, 2)
    if number % 2 == 0:
        number += 1
    while True:
        for divisor in range(3, int(number ** 0.5) + 1, 2):
            if number % divisor == 0:
                break
        else:
            return number
        number += 2


class Node:
    __slots__ = ("key", "value", "next")

    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None


class HashTable:
    """Chained hash table with a public mapping-style API."""

    def __init__(self, size=11, max_load=0.75):
        if not isinstance(size, int) or isinstance(size, bool) or size < 2:
            raise ValueError("size must be an integer at least 2")
        if max_load is not None:
            if (
                isinstance(max_load, bool)
                or not isinstance(max_load, (int, float))
                or max_load <= 0
            ):
                raise ValueError("max_load must be a positive number or None")
        self.size = size
        self.max_load = max_load
        self.buckets = [None for _ in range(size)]
        self._length = 0
        self.collision_count = 0

    @property
    def table(self):
        return self.buckets

    def _index(self, key):
        return horner_hash(key, self.size)

    def put(self, key, value):
        if not isinstance(key, str):
            raise TypeError("key must be a string")
        index = self._index(key)
        node = self.buckets[index]
        while node is not None:
            if node.key == key:
                node.value = value
                return
            node = node.next
        if self.buckets[index] is not None:
            self.collision_count += 1
        self._prepend(index, key, value)

    def _prepend(self, index, key, value):
        node = Node(key, value)
        node.next = self.buckets[index]
        self.buckets[index] = node
        self._length += 1
        if self.max_load is not None and self._length > self.size * self.max_load:
            self._resize()
        return node

    def get(self, key, default=None):
        if not isinstance(key, str):
            raise TypeError("key must be a string")
        node = self.buckets[self._index(key)]
        while node is not None:
            if node.key == key:
                return node.value
            node = node.next
        if default is not None:
            return default
        raise KeyError(key)

    def remove(self, key):
        if not isinstance(key, str):
            raise TypeError("key must be a string")
        index = self._index(key)
        node = self.buckets[index]
        previous = None
        while node is not None:
            if node.key == key:
                if previous is None:
                    self.buckets[index] = node.next
                else:
                    previous.next = node.next
                self._length -= 1
                return node.value
            previous = node
            node = node.next
        raise KeyError(key)

    def contains(self, key):
        try:
            self.get(key)
            return True
        except KeyError:
            return False

    def __contains__(self, key):
        return self.contains(key)

    def __len__(self):
        return self._length

    def __iter__(self):
        for bucket in self.buckets:
            node = bucket
            while node is not None:
                yield node.key
                node = node.next

    def items(self):
        for bucket in self.buckets:
            node = bucket
            while node is not None:
                yield node.key, node.value
                node = node.next

    def _resize(self):
        old_buckets = self.buckets
        self.size = next_prime(self.size * 2)
        self.buckets = [None for _ in range(self.size)]
        self._length = 0
        self.collision_count = 0
        for bucket in old_buckets:
            node = bucket
            while node is not None:
                self.put(node.key, node.value)
                node = node.next


class LinearHashTable:
    """Linear-probing hash table using a tombstone for deletions."""

    _EMPTY = object()
    _TOMB = object()

    def __init__(self, size=11):
        if not isinstance(size, int) or isinstance(size, bool) or size < 2:
            raise ValueError("size must be an integer at least 2")
        self.size = size
        self.keys = [self._EMPTY for _ in range(size)]
        self.values = [None for _ in range(size)]
        self._length = 0

    @property
    def buckets(self):
        return self.keys

    @property
    def table(self):
        return self.keys

    def put(self, key, value):
        if not isinstance(key, str):
            raise TypeError("key must be a string")
        first_tomb = None
        index = horner_hash(key, self.size)
        start = index
        while True:
            if self.keys[index] is self._EMPTY:
                target = first_tomb if first_tomb is not None else index
                self.keys[target] = key
                self.values[target] = value
                self._length += 1
                if self._length > self.size * 0.75:
                    self._resize()
                return
            if self.keys[index] is self._TOMB:
                if first_tomb is None:
                    first_tomb = index
            elif self.keys[index] == key:
                self.values[index] = value
                return
            index = (index + 1) % self.size
            if index == start:
                raise RuntimeError("hash table is full")

    def get(self, key, default=None):
        if not isinstance(key, str):
            raise TypeError("key must be a string")
        index = horner_hash(key, self.size)
        start = index
        while True:
            if self.keys[index] is self._EMPTY:
                if default is not None:
                    return default
                raise KeyError(key)
            if self.keys[index] is not self._TOMB and self.keys[index] == key:
                return self.values[index]
            index = (index + 1) % self.size
            if index == start:
                if default is not None:
                    return default
                raise KeyError(key)

    def remove(self, key):
        if not isinstance(key, str):
            raise TypeError("key must be a string")
        index = horner_hash(key, self.size)
        start = index
        while True:
            if self.keys[index] is self._EMPTY:
                raise KeyError(key)
            if self.keys[index] is not self._TOMB and self.keys[index] == key:
                value = self.values[index]
                self.keys[index] = self._TOMB
                self.values[index] = None
                self._length -= 1
                return value
            index = (index + 1) % self.size
            if index == start:
                raise KeyError(key)

    def contains(self, key):
        try:
            self.get(key)
            return True
        except KeyError:
            return False

    def __contains__(self, key):
        return self.contains(key)

    def __len__(self):
        return self._length

    def __iter__(self):
        for key in self.keys:
            if key is not self._EMPTY and key is not self._TOMB:
                yield key

    def items(self):
        for index, key in enumerate(self.keys):
            if key is not self._EMPTY and key is not self._TOMB:
                yield key, self.values[index]

    def _resize(self):
        old_keys = self.keys
        old_values = self.values
        self.size = next_prime(self.size * 2)
        self.keys = [self._EMPTY for _ in range(self.size)]
        self.values = [None for _ in range(self.size)]
        self._length = 0
        for index, key in enumerate(old_keys):
            if key is not self._EMPTY and key is not self._TOMB:
                self.put(key, old_values[index])


LinearProbingHashTable = LinearHashTable
