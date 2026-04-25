"""
Notes:
- Defines routing decision interface
"""
class RoutingPolicy:
    def next_road(self, engine, vehicle, current_road):
        raise NotImplementedError