from .base import TravelTimePolicy


"""
Notes:
- Simple load-based slowdown
"""
class CongestionPolicy(TravelTimePolicy):
    def __init__(self, alpha=1.0):
        self.alpha = alpha

    def compute(self, engine, road, vehicle):
        base = road.length / vehicle.speed
        congestion = 1 + self.alpha * (road.load / road.capacity)
        return base * congestion