"""
Notes:
- Priority queue for events ordered by time
- Counter ensures deterministic ordering for equal timestamps

TODO:
- FLAG: Missing from_dict implementation. All components must be fully serializable.
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
            "events": [(t, c, e.to_dict()) for t, c, e in self._heap],
            "counter": self._counter,
        }

    @classmethod
    def from_dict(cls, data):
        from core.event import EventRegistry
        obj = cls()
        obj._heap = []
        for t, c, e_dict in data["events"]:
            event = EventRegistry.from_dict(e_dict)
            heapq.heappush(obj._heap, (t, c, event))
        obj._counter = data["counter"]
        return obj