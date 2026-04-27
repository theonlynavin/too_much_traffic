"""
Notes:
- Base class for all passive components

TODO:
- FLAG: Add schema validation for serialized data.
"""
class Component:
    def __init__(self, cid: str):
        self.id = cid

    def to_dict(self):
        return {"id": self.id}

    @classmethod
    def from_dict(cls, data):
        return cls(data["id"])