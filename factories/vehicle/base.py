"""
Notes:
- Base interface for vehicle factories
- Defines the contract for constructing vehicle instances

TODO:
- FLAG: Missing serialization support in base class.
"""
class VehicleFactory:
    def create(self, engine, source, counter):
        raise NotImplementedError

    def to_dict(self):
        return {"type": self.__class__.__name__}

    @classmethod
    def from_dict(cls, data):
        return cls()