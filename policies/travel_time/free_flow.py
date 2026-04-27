"""
Notes:
- Computes traversal time based on road length and vehicle speed
- Assumes free-flow conditions (no congestion impact)

TODO:
- Add congestion-aware travel time computation
"""
from .base import TravelTimePolicy


class FreeFlowPolicy(TravelTimePolicy):
    def compute(self, engine, road, vehicle):
        return road.length / vehicle.speed

    def to_dict(self):
        return {"type": self.__class__.__name__}

    @classmethod
    def from_dict(cls, data):
        return cls()