"""
Base policy interface.

TODO:
- Standardize input/output contract
"""
class Policy:
    def apply(self, engine, **kwargs):
        raise NotImplementedError