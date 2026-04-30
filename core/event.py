class EventRegistry:
    _registry = {}

    @classmethod
    def register(cls, event_cls):
        cls._registry[event_cls.type] = event_cls
        return event_cls

    @classmethod
    def get_class(cls, event_type):
        return cls._registry.get(event_type)

    @classmethod
    def from_dict(cls, data):
        event_type = data.get("type")
        event_cls = cls.get_class(event_type)
        if event_cls is None:
            raise ValueError(f"Unknown event type: {event_type}")
        return event_cls.from_dict(data)

class Event:
    type = "base_event"

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
        return EventRegistry.from_dict(data)