#!python


class Node(object):

    def __init__(self, data):
        """Initialize this node with the given data."""
        self.data = data
        self.next = None

    def __repr__(self):
        """Return a string representation of this node."""
        return f'Node({self.data!r})'


class LinkedList:

    def __init__(self, items=None):
        """Initialize this linked list and append the given items, if any."""
        self.head = None  # First node
        self.tail = None  # Last node
        self.size = 0  # Number of nodes in list
        # Append given items
        if items is not None:
            for item in items:
                self.append(item)

    def __repr__(self):
        """Return a string representation of this linked list."""
        return f'LinkedList({self.items()})'

    def __iter__(self):
        """Iterate over all items in this linked list from head to tail."""
        node = self.head
        while node is not None:
            yield node.data
            node = node.next

    def items(self):
        """Return a list (dynamic array) of all items in this linked list.
        Best and worst case running time: O(n) for n items in the list (length)
        because we always need to loop through all n nodes to get each item."""
        return list(self)

    def is_empty(self):
        """Return a boolean indicating whether this linked list is empty."""
        return self.head is None

    def length(self):
        """Return the length of this linked list in O(1) time.

        The list maintains a `size` counter that is updated by mutating methods,
        so no traversal is required when checking length.
        """
        return self.size

    def append(self, item):
        """Insert the given item at the tail of this linked list.
        Running time: O(1), as tail is tracked directly."""
        new_node = Node(item)
        if self.is_empty():
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self.size += 1

    def prepend(self, item):
        """Insert the given item at the head of this linked list.
        Running time: O(1), as head is tracked directly."""
        new_node = Node(item)
        if self.is_empty():
            self.head = new_node
            self.tail = new_node
        else:
            new_node.next = self.head
            self.head = new_node
        self.size += 1

    def find(self, matcher):
        """Return an item from this linked list if it is present.
        Best case running time: O(1) when head matches.
        Worst case running time: O(n) when no node matches or tail matches."""
        node = self.head
        while node is not None:
            if matcher(node.data):
                return node.data
            node = node.next
        return None

    def delete(self, item):
        """Delete the given item from this linked list, or raise ValueError.
        Best case running time: O(1) when deleting head.
        Worst case running time: O(n) when item is in tail or not present."""
        prev = None
        node = self.head

        while node is not None:
            if node.data == item:
                if prev is None:
                    # Deleting head
                    self.head = node.next
                else:
                    prev.next = node.next

                # If deleting tail, move tail back to prev
                if node is self.tail:
                    self.tail = prev

                # If list is now empty, keep both pointers consistent
                if self.head is None:
                    self.tail = None

                self.size -= 1

                return

            prev = node
            node = node.next

        raise ValueError('Item not found: {}'.format(item))

    def replace(self, old_item, new_item):
        """Replace first occurrence of old_item with new_item in place.

        If old_item is not found, this method makes no changes.
        """
        node = self.head
        while node is not None:
            if node.data == old_item:
                node.data = new_item
                return
            node = node.next


def test_linked_list():
    ll = LinkedList()
    print('list: {}'.format(ll))
    print('\nTesting append:')
    for item in ['A', 'B', 'C']:
        print('append({!r})'.format(item))
        ll.append(item)
        print('list: {}'.format(ll))

    print('head: {}'.format(ll.head))
    print('tail: {}'.format(ll.tail))
    print('length: {}'.format(ll.length()))

    # Enable this after implementing delete method
    delete_implemented = True
    if delete_implemented:
        print('\nTesting delete:')
        for item in ['B', 'C', 'A']:
            print('delete({!r})'.format(item))
            ll.delete(item)
            print('list: {}'.format(ll))

        print('head: {}'.format(ll.head))
        print('tail: {}'.format(ll.tail))
        print('length: {}'.format(ll.length()))


if __name__ == '__main__':
    test_linked_list()
