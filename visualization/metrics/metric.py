class Metric:
    """Base class for all metrics.
    
    Subclasses should set `category` to group themselves in reports.
    The MetricsManager and reporters do NOT need to know the category names
    in advance — they read them from the metric instances at runtime.
    """
    category = "General"   # Override in subclass to control report grouping

    def __init__(self, name=None):
        self.name = name or self.__class__.__name__

    def on_event(self, t, event):
        """Called for every event emitted by the engine."""
        pass

    def reset(self):
        """Reset the metric state."""
        pass

    def summary(self) -> dict:
        """Return a flat dictionary of {key: value} measured values."""
        return {}

    def to_dict(self) -> dict:
        return {"type": self.__class__.__name__, "name": self.name}

    @classmethod
    def from_dict(cls, data):
        return cls(name=data.get("name"))