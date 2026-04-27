"""
Notes:
- Base interface for network topology generators

TODO:
- FLAG: Missing serialization support.
"""
class NetworkFactory:
    def build(self, engine):
        raise NotImplementedError

    def to_dict(self):
        return {"type": self.__class__.__name__}

    @classmethod
    def from_dict(cls, data):
        return cls()