"""
Notes:
- Exponential interarrival process
- Delegates vehicle creation to factory
"""
class PoissonSourcePolicy:
    def __init__(self, rate: float, vehicle_factory):
        if rate <= 0:
            raise ValueError("rate must be positive")

        self.rate = rate
        self.vehicle_factory = vehicle_factory

    def next_interarrival(self, engine):
        return engine.rng.exponential(self.rate)

    def create_vehicle(self, engine, source, counter):
        return self.vehicle_factory.create(engine, source, counter)