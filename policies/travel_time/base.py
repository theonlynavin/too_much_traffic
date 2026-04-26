from ..base_policy import Policy

"""
Notes:
- Defines interface for travel time computation
"""
class TravelTimePolicy(Policy):
    def compute(self, engine, road, vehicle) -> float:
        raise NotImplementedError