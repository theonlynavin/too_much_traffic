"""
Priority queue for events.

Notes:
- Counter ensures deterministic ordering for equal timestamps

TODO:
- Implement proper deserialization with event reconstruction
"""
import heapq

class EventQueue:
    def __init__(self):
        self._heap = []
        self._counter = 0

    def push(self, event):
        heapq.heappush(self._heap, (event.time, self._counter, event))
        self._counter += 1

    def pop(self):
        return heapq.heappop(self._heap)[-1]

    def is_empty(self):
        return len(self._heap) == 0

    def to_dict(self):
        return {
            "events": [e.to_dict() for _, _, e in self._heap],
            "counter": self._counter,
        }