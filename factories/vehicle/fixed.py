from components.vehicle import Vehicle
from .base import VehicleFactory


"""
Notes:
- Produces identical vehicles
"""
class FixedVehicleFactory(VehicleFactory):
    def __init__(self, size: int, destination: str, speed: float):
        if size < 1:
            raise ValueError("size must be >= 1")

        if speed <= 0:
            raise ValueError("speed must be positive")

        self.size = size
        self.destination = destination
        self.speed = speed

    def create(self, engine, source, counter):
        vid = f"{source.id}_veh_{counter}"

        return Vehicle(
            vid,
            source=source.id,
            destination=self.destination,
            size=self.size,
            speed=self.speed
        )