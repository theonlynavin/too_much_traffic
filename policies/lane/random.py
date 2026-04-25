from .base import LanePolicy

class RandomLanePolicy(LanePolicy):
    def choose_lane(self, engine, road, vehicle):
        return engine.rng.randint(0, road.num_lanes - 1)