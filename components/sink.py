"""
Notes:
- End point for vehicles
- Records vehicle exits and total throughput

TODO:
- Track per-vehicle exit times
- Add throughput statistics
"""

class Sink:
    def __init__(self, sid: str, junction_id: str, policy_id: str, pos: tuple[float]):
        self.id = sid
        self.junction_id = junction_id
        self.policy_id = policy_id
        self.pos = pos

    def to_dict(self):
        return {
            "id": self.id,
            "junction_id": self.junction_id,
            "policy_id": self.policy_id,
            "pos": self.pos
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["id"], 
            data.get("junction_id", ""), 
            data.get("policy_id", "counting"), 
            data["pos"]
        )