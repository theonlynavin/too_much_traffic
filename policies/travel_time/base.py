"""
Notes:
- Defines interface for travel time computation
"""
class TravelTimePolicy:
    def compute(self, engine, road, vehicle) -> float:
        raise NotImplementedError