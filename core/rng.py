import random
import math


class RNG:
    def __init__(self, seed: int):
        self._rng = random.Random(seed)

    # ------------------------
    # basic
    # ------------------------

    def uniform(self, a: float, b: float) -> float:
        return self._rng.uniform(a, b)

    def randint(self, a: int, b: int) -> int:
        return self._rng.randint(a, b)

    def random(self) -> float:
        return self._rng.random()

    def choice(self, seq):
        if not seq:
            raise ValueError("empty sequence")
        return self._rng.choice(seq)

    def shuffle(self, seq):
        self._rng.shuffle(seq)
        return seq

    # ------------------------
    # sampling
    # ------------------------

    def sample(self, seq, k: int):
        if k > len(seq):
            raise ValueError("sample larger than population")
        return self._rng.sample(seq, k)

    def choice_n(self, seq, n: int):
        if not seq:
            raise ValueError("empty sequence")
        return [self.choice(seq) for _ in range(n)]

    # ------------------------
    # distributions
    # ------------------------

    def exponential(self, rate: float) -> float:
        if rate <= 0:
            raise ValueError("rate must be positive")
        u = self._rng.random()
        return -math.log(1.0 - u) / rate

    def normal(self, mean: float, std: float) -> float:
        return self._rng.gauss(mean, std)

    def bernoulli(self, p: float) -> bool:
        if not (0 <= p <= 1):
            raise ValueError("p must be in [0,1]")
        return self._rng.random() < p

    # ------------------------
    # weighted sampling
    # ------------------------

    def weighted_choice(self, items, weights):
        if len(items) != len(weights):
            raise ValueError("items and weights must match")

        total = sum(weights)
        if total <= 0:
            raise ValueError("weights must be positive")

        r = self._rng.uniform(0, total)
        acc = 0.0

        for item, w in zip(items, weights):
            acc += w
            if r <= acc:
                return item

        return items[-1]

    def weighted_choice_dict(self, d):
        if not d:
            raise ValueError("empty dict")
        items = list(d.keys())
        weights = list(d.values())
        return self.weighted_choice(items, weights)

    # ------------------------
    # convenience
    # ------------------------

    def uniform_int(self, low: int, high: int):
        return self._rng.randint(low, high)

    def uniform_float(self, low: float, high: float):
        return self._rng.uniform(low, high)

    # ------------------------
    # state (for reproducibility)
    # ------------------------

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