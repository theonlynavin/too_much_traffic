"""
Notes:
- Passive container for road state (lanes, load)
- Multi-lane FIFO structure
"""

class Road:
    def __init__(self, rid: str, start: str, end: str, length: float, capacity: int, num_lanes: int):
        if length <= 0:
            raise ValueError("length must be positive")

        if capacity < 1:
            raise ValueError("capacity must be >= 1")

        if num_lanes < 1:
            raise ValueError("num_lanes must be >= 1")

        self.id = rid
        self.start = start
        self.end = end
        self.length = length
        self.capacity = capacity
        self.num_lanes = num_lanes

    def to_dict(self):
        return {
            "id": self.id,
            "start": self.start,
            "end": self.end,
            "length": self.length,
            "capacity": self.capacity,
            "num_lanes": self.num_lanes
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls(
            data["id"],
            data["start"],
            data["end"],
            data["length"],
            data["capacity"],
            data["num_lanes"]
        )
        return obj