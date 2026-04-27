"""
Notes:
- Exponential interarrival process for vehicle spawning
- Delegates vehicle property generation to a factory

TODO:
- FLAG: Missing to_dict/from_dict implementation.
- Support time-varying rates
"""
from .base import SourcePolicy


class PoissonSourcePolicy(SourcePolicy):
    def __init__(self, rate: float, vehicle_factory):
        if rate <= 0:
            raise ValueError("rate must be positive")

        self.rate = rate
        self.vehicle_factory = vehicle_factory

    def next_interarrival(self, engine):
        return engine.rng.exponential(self.rate)

    def create_vehicle(self, engine, source, counter):
        return self.vehicle_factory.create(engine, source, counter)

    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "rate": self.rate,
            "vehicle_factory": self.vehicle_factory.to_dict()
        }

    @classmethod
    def from_dict(cls, data):
        # NOTE: vehicle_factory must be reconstructed elsewhere or handled via registry
        raise NotImplementedError("Requires factory reconstruction logic")