from .metric import Metric
from collections import defaultdict


class RoadLoadMetric(Metric):
    """Tracks load (occupancy) per road over time, and peak/average congestion."""
    category = "Network Flow"

    def __init__(self, name=None):
        super().__init__(name or "RoadLoadMetric")
        # road_id -> list of (time, load_after_event)
        self.load_history = defaultdict(list)
        self._current_load = defaultdict(int)

    def reset(self):
        self.load_history.clear()
        self._current_load.clear()

    def on_event(self, t, event):
        etype = event.get("type")

        if etype == "spawn":
            rid = event.get("road_id")
            if rid:
                self._current_load[rid] += 1
                self.load_history[rid].append((t, self._current_load[rid]))

        elif etype in ("transfer", "exit"):
            rid = event.get("from_road")
            if rid:
                self._current_load[rid] = max(0, self._current_load[rid] - 1)
                self.load_history[rid].append((t, self._current_load[rid]))

    def summary(self):
        res = {}
        for rid, history in self.load_history.items():
            if not history:
                continue
            loads = [load for _, load in history]
            res[f"road_{rid}_peak_load"] = max(loads)
            res[f"road_{rid}_avg_load"] = round(sum(loads) / len(loads), 3)
            res[f"road_{rid}_current_load"] = self._current_load[rid]
        return res
