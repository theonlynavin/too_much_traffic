from components.vehicle import Vehicle
from .base import VehicleFactory


"""
Notes:
- Uses user-provided functions for size and destination
"""
class DistributionVehicleFactory(VehicleFactory):
    def __init__(self, size_fn, destination_fn):
        self.size_fn = size_fn
        self.destination_fn = destination_fn

    def create(self, engine, source, counter):
        vid = f"{source.id}_veh_{counter}"

        size = self.size_fn(engine, source)
        destination = self.destination_fn(engine, source)

        if size < 1:
            raise ValueError("size must be >= 1")

        return Vehicle(
            vid,
            source=source.id,
            destination=destination,
            size=size
        )