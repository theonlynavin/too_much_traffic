from components.vehicle import Vehicle
from .base import VehicleFactory


"""
Notes:
- Uses user-provided functions for size and destination
"""
class DistributionVehicleFactory(VehicleFactory):
    def __init__(self, kind_fn, size_fn, speed_fn, destination_fn):
        self.kind_fn = kind_fn
        self.size_fn = size_fn
        self.speed_fn = speed_fn
        self.destination_fn = destination_fn

    def create(self, engine, source, counter):
        vid = f"{source.id}_veh_{counter}"

        kind = self.kind_fn(engine, source)
        size = self.size_fn(engine, source)
        speed = self.speed_fn(engine, source)
        destination = self.destination_fn(engine, source)

        if size < 1:
            raise ValueError("size must be >= 1")
        if speed <= 0:
            raise ValueError("speed must be >= 0")

        return Vehicle(
            vid,
            source=source.id,
            destination=destination,
            kind=kind,
            size=size,
            speed=speed
        )