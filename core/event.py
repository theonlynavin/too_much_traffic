"""
Notes:
- Events are the only active units in the system
- Event type must be stable and ASCII-only

TODO:
- Implement registry for type to class mapping
"""
class Event:
    type = "base_event"  # must be overridden with ASCII string

    def __init__(self, time: float):
        self.time = time

    def process(self, engine):
        raise NotImplementedError

    def to_dict(self):
        return {
            "type": self.type,
            "time": self.time,
            "data": self._data_dict()
        }

    def _data_dict(self):
        return {}

    @classmethod
    def from_dict(cls, data):
        raise NotImplementedError