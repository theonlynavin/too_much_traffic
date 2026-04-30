from .metric import Metric
from collections import defaultdict


class TravelTimeMetric(Metric):
    """Tracks per-vehicle travel time from spawn to exit."""
    category = "Travel Time"

    def __init__(self, name=None):
        super().__init__(name or "TravelTimeMetric")
        self.spawn_info = {}  # vid -> (spawn_time, source_id, destination)
        self.travel_times = []  # all completed travel times
        self.source_stats = defaultdict(lambda: {"total_time": 0.0, "count": 0, "min": float("inf"), "max": 0.0})
        self.destination_stats = defaultdict(lambda: {"total_time": 0.0, "count": 0})

    def reset(self):
        self.spawn_info.clear()
        self.travel_times.clear()
        self.source_stats.clear()
        self.destination_stats.clear()

    def on_event(self, t, event):
        etype = event.get("type")

        if etype == "spawn":
            vid = event["vehicle_id"]
            self.spawn_info[vid] = (t, event.get("source_id"), event.get("destination"))

        elif etype == "exit":
            vid = event["vehicle_id"]
            if vid in self.spawn_info:
                t0, src, dest = self.spawn_info.pop(vid)
                dt = t - t0
                self.travel_times.append(dt)

                st = self.source_stats[src]
                st["total_time"] += dt
                st["count"] += 1
                st["min"] = min(st["min"], dt)
                st["max"] = max(st["max"], dt)

                self.destination_stats[dest]["total_time"] += dt
                self.destination_stats[dest]["count"] += 1

    def summary(self):
        n = len(self.travel_times)
        avg = sum(self.travel_times) / n if n > 0 else 0.0
        mn = min(self.travel_times) if n > 0 else 0.0
        mx = max(self.travel_times) if n > 0 else 0.0

        res = {
            "vehicle_completed_trips": n,
            "vehicle_avg_travel_time": round(avg, 4),
            "vehicle_min_travel_time": round(mn, 4),
            "vehicle_max_travel_time": round(mx, 4),
        }
        for src, st in self.source_stats.items():
            c = st["count"]
            a = st["total_time"] / c if c > 0 else 0.0
            res[f"source_{src}_avg_travel_time"] = round(a, 4)
            res[f"source_{src}_min_travel_time"] = round(st["min"] if c > 0 else 0.0, 4)
            res[f"source_{src}_max_travel_time"] = round(st["max"], 4)
        return res