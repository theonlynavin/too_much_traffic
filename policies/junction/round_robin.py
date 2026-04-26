from .base import JunctionPolicy


class RoundRobinJunctionPolicy(JunctionPolicy):
    def __init__(self):
        self._index = 0

    def select_incoming(self, engine, junction):
        roads = [
            rid for rid in junction.queues
            if junction.peek(rid) is not None
        ]

        if not roads:
            return None   

        # wrap index safely
        self._index = self._index % len(roads)

        rid = roads[self._index]
        self._index = (self._index + 1) % len(roads)

        return rid

    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "index": self._index,
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls()
        obj._index = data.get("index", 0)
        return obj