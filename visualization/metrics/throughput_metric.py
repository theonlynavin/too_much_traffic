from .metric import Metric
from collections import defaultdict


class ThroughputMetric(Metric):
    """Tracks how many vehicles reach each sink and the overall flow rate."""
    category = "Throughput"

    def __init__(self, name=None, window=5.0):
        super().__init__(name or "ThroughputMetric")
        self.window = window
        self.exit_times = []
        self.sink_counts = defaultdict(int)
        self.sink_times = defaultdict(list)
        self.source_spawn_counts = defaultdict(int)
        self.source_drop_counts = defaultdict(int)

    def reset(self):
        self.exit_times.clear()
        self.sink_counts.clear()
        self.sink_times.clear()
        self.source_spawn_counts.clear()
        self.source_drop_counts.clear()

    def on_event(self, t, event):
        etype = event.get("type")
        if etype == "exit":
            self.exit_times.append(t)
            sid = event["sink_id"]
            self.sink_counts[sid] += 1
            self.sink_times[sid].append(t)

        elif etype == "spawn":
            self.source_spawn_counts[event["source_id"]] += 1

        elif etype == "dropped":
            self.source_drop_counts[event.get("source_id", "unknown")] += 1

    def _rate(self, times):
        if not times:
            return 0.0
        t_now = times[-1]
        recent = [t for t in times if t_now - t <= self.window]
        return len(recent) / self.window

    def summary(self):
        res = {
            "total_vehicles_exited": len(self.exit_times),
            "total_throughput_rate": round(self._rate(self.exit_times), 4),
        }
        for sid, times in self.sink_times.items():
            res[f"sink_{sid}_total_received"] = self.sink_counts[sid]
            res[f"sink_{sid}_recent_rate"] = round(self._rate(times), 4)
        for src, count in self.source_spawn_counts.items():
            res[f"source_{src}_spawned"] = count
        for src, count in self.source_drop_counts.items():
            res[f"source_{src}_dropped"] = count
        return res