"""
Notes:
- Speed determines traversal time across roads
- Size contributes to road capacity usage
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
        return cls(
            data["id"],
            data["source"],
            data["destination"],
            data["kind"],
            data["size"],
            data["speed"]
        )