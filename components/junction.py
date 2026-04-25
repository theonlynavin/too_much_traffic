"""
Notes:
- Passive node connecting roads
"""
class Junction:
    def __init__(self, jid: str, incoming: list[str], outgoing: list[str], pos: tuple[float]):
        self.id = jid
        self.incoming = incoming
        self.outgoing = outgoing
        self.pos = pos # (x, y)

    def to_dict(self):
        return {
            "id": self.id,
            "incoming": self.incoming,
            "outgoing": self.outgoing,
            "pos": self.pos
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["id"],
            data["incoming"],
            data["outgoing"],
            data["pos"]
        )