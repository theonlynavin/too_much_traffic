from .metric import Metric
from collections import defaultdict


class VehicleKindMetric(Metric):
    """Tracks statistics broken down by vehicle kind (car, truck, bike, etc.)."""
    category = "Vehicle Breakdown"

    def __init__(self, name=None):
        super().__init__(name or "VehicleKindMetric")
        # kind -> {spawned, exited, total_time, dropped}
        self.kind_stats = defaultdict(lambda: {"spawned": 0, "exited": 0, "dropped": 0, "total_time": 0.0})
        self._spawn_times = {}  # vid -> (kind, spawn_time)

    def reset(self):
        self.kind_stats.clear()
        self._spawn_times.clear()

    def on_event(self, t, event):
        etype = event.get("type")

        if etype == "spawn":
            vid = event["vehicle_id"]
            kind = event.get("kind", "unknown")
            self.kind_stats[kind]["spawned"] += 1
            self._spawn_times[vid] = (kind, t)

        elif etype == "exit":
            vid = event["vehicle_id"]
            if vid in self._spawn_times:
                kind, t0 = self._spawn_times.pop(vid)
                self.kind_stats[kind]["exited"] += 1
                self.kind_stats[kind]["total_time"] += t - t0

        elif etype == "dropped":
            kind = event.get("kind", "unknown")
            self.kind_stats[kind]["dropped"] += 1

    def summary(self):
        res = {}
        for kind, stats in sorted(self.kind_stats.items()):
            exited = stats["exited"]
            avg = stats["total_time"] / exited if exited > 0 else 0.0
            res[f"vehicle_{kind}_spawned"] = stats["spawned"]
            res[f"vehicle_{kind}_exited"] = exited
            res[f"vehicle_{kind}_dropped"] = stats["dropped"]
            res[f"vehicle_{kind}_avg_travel_time"] = round(avg, 4)
        return res
