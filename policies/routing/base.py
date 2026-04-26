from ..base_policy import Policy

"""
Notes:
- Defines routing decision interface
"""
class RoutingPolicy(Policy):
    def next_road(self, engine, vehicle, current_road):
        raise NotImplementedError