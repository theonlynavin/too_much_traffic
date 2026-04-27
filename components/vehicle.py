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
        self.arrival_time = float("inf")  # time vehicle last reached front of a road
        self.travel_end_time = -1.0

    def to_dict(self):
        return {
            "id": self.id,
            "source": self.source,
            "destination": self.destination,
            "kind": self.kind,
            "size": self.size,
            "speed": self.speed,
            "arrival_time": self.arrival_time,
            "travel_end_time": self.travel_end_time
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
        obj.arrival_time = data.get("arrival_time", float("inf"))
        obj.travel_end_time = data.get("travel_end_time", -1.0)
        return obj