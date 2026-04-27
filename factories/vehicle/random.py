"""
Notes:
- Constructs vehicles with randomized properties (destination, type)
- Uses the engine's RNG for reproducibility

TODO:
- FLAG: Missing serialization support.
"""
from components.vehicle import Vehicle
from .base import VehicleFactory

class RandomVehicleFactory(VehicleFactory):
    def __init__(self, destinations, kinds):
        self.destinations = destinations
        self.kinds = kinds

    def create(self, engine, source, counter):
        vid = f"{source.id}_{counter}"

        dest = engine.rng.choice(self.destinations)
        kind = engine.rng.choice(list(self.kinds.keys()))

        props = self.kinds[kind]

        return Vehicle(
            vid=vid,
            source=source.id,
            destination=dest,
            kind=kind,
            size=props["size"],
            speed=props["speed"]
        )

    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "destinations": self.destinations,
            "kinds": self.kinds
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            destinations=data["destinations"],
            kinds=data["kinds"]
        )