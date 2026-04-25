"""
Notes:
- All randomness in the system must go through this class
- Wraps Python random.Random but does not expose it
"""
import random
import math


class RNG:
    def __init__(self, seed: int):
        self._rng = random.Random(seed)

    def uniform(self, a: float, b: float) -> float:
        return self._rng.uniform(a, b)

    def choice(self, seq):
        return self._rng.choice(seq)

    def randint(self, a: int, b: int) -> int:
        return self._rng.randint(a, b)

    def random(self) -> float:
        return self._rng.random()

    def exponential(self, rate: float) -> float:
        if rate <= 0:
            raise ValueError("rate must be positive")
        u = self._rng.random()
        return -math.log(1.0 - u) / rate

    def get_state(self):
        return self._rng.getstate()

    def set_state(self, state):
        self._rng.setstate(state)

    def to_dict(self):
        return {"state": self.get_state()}

    @classmethod
    def from_dict(cls, data):
        obj = cls(0)
        obj.set_state(data["state"])
        return obj