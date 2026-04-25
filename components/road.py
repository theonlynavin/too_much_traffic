"""
Notes:
- Multi-lane FIFO
- Each lane is an independent queue
- No lane changing (yet)

TODO:
- Lane changing
- Overtaking
- Lane-specific speed / behavior
"""
from collections import deque


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

        self.lanes = [deque() for _ in range(num_lanes)]
        self.load = 0

    def has_space_for(self, size: int) -> bool:
        return self.load + size <= self.capacity

    def add_vehicle(self, vehicle, lane: int):
        if not (0 <= lane < self.num_lanes):
            raise ValueError("invalid lane")

        if not self.has_space_for(vehicle.size):
            raise ValueError("capacity exceeded")

        self.lanes[lane].append(vehicle.id)
        self.load += vehicle.size

    def is_front(self, vehicle_id: str, lane: int) -> bool:
        q = self.lanes[lane]
        return len(q) > 0 and q[0] == vehicle_id

    def remove_vehicle(self, vehicle, lane: int):
        q = self.lanes[lane]

        if len(q) == 0:
            raise ValueError("lane empty")

        if q[0] != vehicle.id:
            raise ValueError("only front can leave")

        q.popleft()
        self.load -= vehicle.size

    def to_dict(self):
        return {
            "id": self.id,
            "start": self.start,
            "end": self.end,
            "length": self.length,
            "capacity": self.capacity,
            "num_lanes": self.num_lanes,
            "lanes": [list(q) for q in self.lanes],
            "load": self.load
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
        obj.lanes = [deque(q) for q in data.get("lanes", [])]
        obj.load = data.get("load", 0)
        return obj