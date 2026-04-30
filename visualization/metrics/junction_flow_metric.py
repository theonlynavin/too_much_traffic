from .metric import Metric
from collections import defaultdict


class JunctionFlowMetric(Metric):
    """Tracks vehicle transfers through each junction."""
    category = "Network Flow"

    def __init__(self, name=None):
        super().__init__(name or "JunctionFlowMetric")
        self.junction_counts = defaultdict(int)
        self.road_flows = defaultdict(lambda: defaultdict(int))

    def reset(self):
        self.junction_counts.clear()
        self.road_flows.clear()

    def on_event(self, t, event):
        if event.get("type") == "transfer":
            jid = event["junction_id"]
            self.junction_counts[jid] += 1
            self.road_flows[jid][event["from_road"]] += 1

    def summary(self):
        res = {}
        for jid, total in sorted(self.junction_counts.items(), key=lambda x: -x[1]):
            res[f"junction_{jid}_total"] = total
            for rid, count in self.road_flows[jid].items():
                res[f"junction_{jid}_from_{rid}"] = count
        return res
