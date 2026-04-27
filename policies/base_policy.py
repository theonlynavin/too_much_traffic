"""
Notes:
- Base interface for all pluggable policies
- All policies must be serializable via to_dict/from_dict

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