from collections import defaultdict, deque


class Junction:
    def __init__(self, jid: str, incoming: list[str], outgoing: list[str], pos: tuple[float]):
        self.id = jid
        self.incoming = incoming
        self.outgoing = outgoing
        self.pos = pos

        self.queues = defaultdict(deque)
        
    def enqueue(self, rid: str, vid: str, lane: int):
        if rid not in self.incoming:
            raise RuntimeError(f"{rid} not incoming to {self.id}")  # keep this check

        self.queues[rid].append((vid, lane))

    def peek(self, rid: str):
        q = self.queues[rid]
        return q[0] if q else None

    def pop(self, rid: str):
        q = self.queues[rid]
        if not q:
            raise ValueError("empty queue")
        return q.popleft()

    def has_waiting(self):
        return any(q for q in self.queues.values())

    def to_dict(self):
        return {
            "id": self.id,
            "incoming": self.incoming,
            "outgoing": self.outgoing,
            "pos": self.pos,
            "queues": {rid: list(q) for rid, q in self.queues.items()},
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls(
            data["id"],
            data["incoming"],
            data["outgoing"],
            data["pos"],
        )
        obj.queues = defaultdict(deque, {
            rid: deque(q) for rid, q in data.get("queues", {}).items()
        })
        return obj