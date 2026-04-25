from .base import RoutingPolicy


"""
Notes:
- Always selects the only outgoing road
"""
class FixedRoutingPolicy(RoutingPolicy):
    def next_road(self, engine, vehicle, current_road):
        junction = engine.components[current_road.end]

        if len(junction.outgoing) == 0:
            return None

        if len(junction.outgoing) > 1:
            raise ValueError("Ambiguous routing")

        return engine.components[junction.outgoing[0]]