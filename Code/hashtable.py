#!python

from linkedlist import LinkedList


class HashTable(object):

    def __init__(self, init_size=8):
        """Initialize this hash table with the given initial size."""
        # Create a new list (used as fixed-size array) of empty linked lists
        self.buckets = []
        for i in range(init_size):
            self.buckets.append(LinkedList())
        self.size = 0

    def __str__(self):
        """Return a formatted string representation of this hash table."""
        items = []
        for key, val in self.items():
            items.append('{!r}: {!r}'.format(key, val))
        return '{' + ', '.join(items) + '}'

    def __repr__(self):
        """Return a string representation of this hash table."""
        return 'HashTable({!r})'.format(self.items())

    def _bucket_index(self, key):
        """Return the bucket index where the given key would be stored."""
        # Calculate the given key's hash code and transform into bucket index
        return hash(key) % len(self.buckets)

    def keys(self):
        """Return a list of all keys in this hash table.
        Running time: O(b + n) where b is bucket count and n is entry count."""
        # Collect all keys in each bucket
        all_keys = []
        for bucket in self.buckets:
            for key, value in bucket.items():
                all_keys.append(key)
        return all_keys

    def values(self):
        """Return a list of all values in this hash table.
        Running time: O(b + n) where b is bucket count and n is entry count."""
        # Collect all values in each bucket
        all_values = []
        for bucket in self.buckets:
            for key, value in bucket.items():
                all_values.append(value)
        return all_values

    def items(self):
        """Return a list of all items (key-value pairs) in this hash table.
        Running time: O(b + n) where b is bucket count and n is entry count."""
        # Collect all pairs of key-value entries in each bucket
        all_items = []
        for bucket in self.buckets:
            all_items.extend(bucket.items())
        return all_items

    def length(self):
        """Return the number of key-value entries in O(1) time."""
        return self.size

    def contains(self, key):
        """Return True if this hash table contains the given key, or False.
        Best case running time: O(1) if key is first in bucket.
        Worst case running time: O(n) if many collisions occur in one bucket."""
        bucket_index = self._bucket_index(key)
        bucket = self.buckets[bucket_index]
        return bucket.find(lambda entry: entry[0] == key) is not None

    def get(self, key):
        """Return the value associated with the given key, or raise KeyError.
        Best case running time: O(1) if key is first in bucket.
        Worst case running time: O(n) if many collisions occur in one bucket."""
        bucket_index = self._bucket_index(key)
        bucket = self.buckets[bucket_index]
        entry = bucket.find(lambda pair: pair[0] == key)
        if entry is None:
            raise KeyError('Key not found: {}'.format(key))
        return entry[1]

    def set(self, key, value):
        """Insert or update the given key with its associated value.
        Best case running time: O(1) for empty/small bucket.
        Worst case running time: O(n) if many collisions occur in one bucket."""
        bucket_index = self._bucket_index(key)
        bucket = self.buckets[bucket_index]

        old_entry = bucket.find(lambda pair: pair[0] == key)
        if old_entry is not None:
            bucket.delete(old_entry)
            bucket.append((key, value))
        else:
            bucket.append((key, value))
            self.size += 1

    def delete(self, key):
        """Delete the given key from this hash table, or raise KeyError.
        Best case running time: O(1) if key is first in bucket.
        Worst case running time: O(n) if many collisions occur in one bucket."""
        bucket_index = self._bucket_index(key)
        bucket = self.buckets[bucket_index]

        entry = bucket.find(lambda pair: pair[0] == key)
        if entry is None:
            raise KeyError('Key not found: {}'.format(key))

        bucket.delete(entry)
        self.size -= 1

def test_hash_table():
    ht = HashTable()
    print('hash table: {}'.format(ht))

    print('\nTesting set:')
    for key, value in [('I', 1), ('V', 5), ('X', 10)]:
        print('set({!r}, {!r})'.format(key, value))
        ht.set(key, value)
        print('hash table: {}'.format(ht))

    print('\nTesting get:')
    for key in ['I', 'V', 'X']:
        value = ht.get(key)
        print('get({!r}): {!r}'.format(key, value))

    print('contains({!r}): {}'.format('X', ht.contains('X')))
    print('length: {}'.format(ht.length()))

    # Enable this after implementing delete method
    delete_implemented = True
    if delete_implemented:
        print('\nTesting delete:')
        for key in ['I', 'V', 'X']:
            print('delete({!r})'.format(key))
            ht.delete(key)
            print('hash table: {}'.format(ht))

        print('contains(X): {}'.format(ht.contains('X')))
        print('length: {}'.format(ht.length()))


if __name__ == '__main__':
    test_hash_table()
