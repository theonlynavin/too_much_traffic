"""
Notes:
- Selects the lane for a vehicle entering a road
- Currently picks the lane with the fewest vehicles (Least Loaded)

TODO:
- FLAG: Missing to_dict/from_dict implementation.
"""
from .base import LanePolicy

class LeastLoadedLanePolicy(LanePolicy):
    def choose_lane(self, engine, road, vehicle):
        state_policy = engine.policies["state"]
        sizes = [state_policy.get_lane_size(engine, road.id, i) for i in range(road.num_lanes)]
        return sizes.index(min(sizes))

    def to_dict(self):
        return {"type": self.__class__.__name__}

    @classmethod
    def from_dict(cls, data):
        return cls()