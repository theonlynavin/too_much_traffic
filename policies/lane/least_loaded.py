from .base import LanePolicy

class LeastLoadedLanePolicy(LanePolicy):
    def choose_lane(self, engine, road, vehicle):
        sizes = [len(q) for q in road.lanes]
        return sizes.index(min(sizes))