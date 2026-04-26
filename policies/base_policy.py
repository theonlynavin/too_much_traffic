"""
Base policy interface.

TODO:
- Standardize input/output contract
"""
class Policy:    
    def to_dict(self):
        return {
            "type": self.__class__.__name__,
        }

    @classmethod
    def from_dict(cls, data):
        return cls()