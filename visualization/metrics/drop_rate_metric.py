from .metric import Metric
from collections import defaultdict


class DropRateMetric(Metric):
    """Tracks how many vehicles are dropped (capacity full or no path) vs spawned."""
    category = "Throughput"

    def __init__(self, name=None):
        super().__init__(name or "DropRateMetric")
        self.total_spawned = 0
        self.total_dropped_capacity = 0
        self.total_dropped_no_path = 0
        self.source_drops = defaultdict(lambda: {"capacity": 0, "no_path": 0})

    def reset(self):
        self.total_spawned = 0
        self.total_dropped_capacity = 0
        self.total_dropped_no_path = 0
        self.source_drops.clear()

    def on_event(self, t, event):
        etype = event.get("type")

        if etype == "spawn":
            self.total_spawned += 1

        elif etype == "dropped":
            reason = event.get("reason", "unknown")
            src = event.get("source_id", "unknown")
            if reason == "capacity_full":
                self.total_dropped_capacity += 1
                self.source_drops[src]["capacity"] += 1
            elif reason == "no_path":
                self.total_dropped_no_path += 1
                self.source_drops[src]["no_path"] += 1

    def summary(self):
        total_attempted = self.total_spawned + self.total_dropped_capacity + self.total_dropped_no_path
        drop_rate = (self.total_dropped_capacity + self.total_dropped_no_path) / total_attempted if total_attempted > 0 else 0.0

        res = {
            "total_vehicles_attempted": total_attempted,
            "total_vehicles_spawned": self.total_spawned,
            "total_dropped_capacity_full": self.total_dropped_capacity,
            "total_dropped_no_path": self.total_dropped_no_path,
            "overall_drop_rate": round(drop_rate, 4),
        }
        for src, drops in self.source_drops.items():
            if drops["capacity"]:
                res[f"source_{src}_dropped_capacity"] = drops["capacity"]
            if drops["no_path"]:
                res[f"source_{src}_dropped_no_path"] = drops["no_path"]
        return res
