"""
Notes:
- No generation logic here, handled via events

TODO:
- Support stochastic generation (Poisson)
- Add vehicle template (default destination, type)
"""
class Source:
    def __init__(self, sid: str, road_id: str, policy_id: float, pos: tuple[float]):
        self.id = sid
        self.road_id = road_id
        self.policy_id = policy_id
        self.pos = pos

    def to_dict(self):
        return {
            "id": self.id,
            "road_id": self.road_id,
            "policy_id": self.policy_id,
            "pos": self.pos
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["id"], data["road_id"], data["policy_id"], data["pos"])