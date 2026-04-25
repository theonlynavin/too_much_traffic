from .base import RoutingPolicy


class RandomRoutingPolicy(RoutingPolicy):
    def next_road(self, engine, vehicle, current_road):
        junction = engine.components[current_road.end]

        if not junction.outgoing:
            return None

        rid = engine.rng.choice(junction.outgoing)
        return engine.components[rid]