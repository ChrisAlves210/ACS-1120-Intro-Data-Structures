#!python
"""Queue implementation with O(1) enqueue and dequeue."""

from linkedlist import Node


class Queue(object):
    """FIFO queue backed by linked nodes."""

    def __init__(self, items=None):
        self.head = None
        self.tail = None
        self.size = 0

        if items is not None:
            for item in items:
                self.enqueue(item)

    def __len__(self):
        return self.size

    def __iter__(self):
        node = self.head
        while node is not None:
            yield node.data
            node = node.next

    def is_empty(self):
        return self.size == 0

    def enqueue(self, item):
        """Add item to back of queue in O(1)."""
        new_node = Node(item)
        if self.is_empty():
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self.size += 1

    def dequeue(self):
        """Remove and return item at front of queue in O(1)."""
        if self.is_empty():
            raise IndexError("Cannot dequeue from an empty queue")

        front_item = self.head.data
        self.head = self.head.next
        self.size -= 1

        if self.head is None:
            self.tail = None

        return front_item
