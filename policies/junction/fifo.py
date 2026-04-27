from .base import JunctionPolicy


class FIFOJunctionPolicy(JunctionPolicy):
    def select_incoming(self, engine, junction):
        best_rid = None
        best_time = float("inf")

        for rid in junction.incoming:
            q = junction.queues[rid]
            if not q:
                continue

            vid, _ = q[0]
            vehicle = engine.components.get(vid)
            if vehicle is None:
                continue
            t = getattr(vehicle, "arrival_time", float("inf"))

            if t < best_time:
                best_time = t
                best_rid = rid

        return best_rid