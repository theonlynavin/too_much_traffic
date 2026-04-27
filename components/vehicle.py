"""
Notes:
- Passive data container for vehicle properties
- Speed and size are used by policies to compute traversal and capacity

TODO:
- FLAG: Internal time tracking (arrival_time, travel_end_time) violates "No internal time tracking" rule.
- FLAG: No hidden state - arrival_time and travel_end_time are being modified externally by events.
"""
class Vehicle:
    def __init__(self, vid: str, source: str, destination: str, kind : str, size: int, speed: float):
        if size < 1:
            raise ValueError("size must be >= 1")

        if speed <= 0:
            raise ValueError("speed must be positive")

        self.id = vid
        self.source = source
        self.destination = destination
        self.kind = kind
        self.size = size
        self.speed = speed

    def to_dict(self):
        return {
            "id": self.id,
            "source": self.source,
            "destination": self.destination,
            "kind": self.kind,
            "size": self.size,
            "speed": self.speed
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls(
            data["id"],
            data["source"],
            data["destination"],
            data["kind"],
            data["size"],
            data["speed"]
        )
        return obj