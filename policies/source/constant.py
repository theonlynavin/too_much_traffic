from .base import SourcePolicy

"""
Notes:
- Deterministic interarrival process
- Delegates vehicle creation to factory
"""
class ConstantSourcePolicy(SourcePolicy):
    def __init__(self, rate: float, vehicle_factory):
        if rate <= 0:
            raise ValueError("rate must be positive")

        self.rate = rate
        self.vehicle_factory = vehicle_factory

    def next_interarrival(self, engine):
        return 1.0 / self.rate

    def create_vehicle(self, engine, source, counter):
        return self.vehicle_factory.create(engine, source, counter)