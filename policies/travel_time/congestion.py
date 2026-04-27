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
        state_policy = engine.policies["state"]
        load = state_policy.get_load(engine, road.id)
        congestion = 1 + self.alpha * (load / road.capacity)
        return base * congestion