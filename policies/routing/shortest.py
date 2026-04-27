"""
Notes:
- Determines the next road for a vehicle using the network's routing table
- Shortest path is pre-computed by the Network

TODO:
- FLAG: Policy reaches into engine.components[rid] directly.
- Support dynamic re-routing based on live traffic
"""
from .base import RoutingPolicy


class ShortestPathRoutingPolicy(RoutingPolicy):
    def __init__(self, on_no_path="error"):
        self.on_no_path = on_no_path  # "error" | "drop"

    def next_road(self, engine, vehicle, current_road):
        network = engine.network

        rid = network.next_road(
            current_road.end,
            vehicle.destination
        )

        if rid is None:
            if self.on_no_path == "drop":
                return None

            raise ValueError(
                f"No path from {current_road.end} to {vehicle.destination}"
            )

        return engine.components[rid]

    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "on_no_path": self.on_no_path,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data.get("on_no_path", "error")
        )