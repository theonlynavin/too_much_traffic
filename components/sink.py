"""
Notes:
- End point for vehicles
- Records vehicle exits and total throughput

TODO:
- Track per-vehicle exit times
- Add throughput statistics
"""

class Sink:
    def __init__(self, sid: str, pos: tuple[float]):
        self.id = sid
        self.received = 0
        self.received_ids = set()
        self.pos = pos

    def record(self, vehicle_id):
        if vehicle_id in self.received_ids:
            raise ValueError("Vehicle exited twice")

        self.received_ids.add(vehicle_id)
        self.received += 1

    def to_dict(self):
        return {
            "id": self.id,
            "received": self.received,
            "received_ids": list(self.received_ids),
            "pos": self.pos
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls(data["id"], data["pos"])
        obj.received = data["received"]
        obj.received_ids = set(data.get("received_ids", []))
        return obj