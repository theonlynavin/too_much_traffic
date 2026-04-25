from .base import TravelTimePolicy


"""
Notes:
- Pure physics: no congestion
"""
class FreeFlowPolicy(TravelTimePolicy):
    def compute(self, engine, road, vehicle):
        return road.length / vehicle.speed