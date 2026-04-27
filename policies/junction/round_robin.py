"""
Notes:
- Selects which incoming road gets to move a vehicle through the junction
- Uses round-robin scheduling to ensure fairness

TODO:
- FLAG: Stores internal state (_indices) which must be fully serialized.
- Add weighted round-robin based on road priority
"""
from .base import JunctionPolicy


class RoundRobinJunctionPolicy(JunctionPolicy):
    def __init__(self):
        self._indices = {}  # junction_id -> int

    def select_incoming(self, engine, junction):
        state_policy = engine.policies["state"]
        roads = [
            rid for rid in junction.incoming
            if state_policy.peek_junction(engine, junction.id, rid) is not None
        ]

        if not roads:
            return None

        idx = self._indices.get(junction.id, 0) % len(roads)
        rid = roads[idx]
        self._indices[junction.id] = (idx + 1) % len(roads)

        return rid

    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "indices": self._indices,
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls()
        obj._indices = data.get("indices", {})
        return obj