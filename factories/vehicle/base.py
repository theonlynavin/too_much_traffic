"""
Notes:
- Factory defines how vehicles are constructed
"""
class VehicleFactory:
    def create(self, engine, source, counter):
        raise NotImplementedError