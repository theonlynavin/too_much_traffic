from ..base_policy import Policy

class LanePolicy(Policy):
    def choose_lane(self, engine, road, vehicle) -> int:
        raise NotImplementedError