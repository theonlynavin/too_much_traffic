from .base import JunctionPolicy


class RandomJunctionPolicy(JunctionPolicy):
    def select_incoming(self, engine, junction):
        candidates = [
            rid for rid in junction.incoming
            if junction.queues[rid]
        ]

        if not candidates:
            return None

        return engine.rng.choice(candidates)