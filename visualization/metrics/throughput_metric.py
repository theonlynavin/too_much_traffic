from .metric import Metric


class ThroughputMetric(Metric):
    def __init__(self):
        self.exit_times = []
        self.sink_stats = {} # sink_id -> list of exit times

    def on_event(self, t, event):
        if event["type"] == "exit":
            self.exit_times.append(t)
            sid = event["sink_id"]
            if sid not in self.sink_stats:
                self.sink_stats[sid] = []
            self.sink_stats[sid].append(t)

    def current_rate(self, times, window=5.0):
        if not times:
            return 0.0

        t_now = times[-1]
        recent = [t for t in times if t_now - t <= window]

        return len(recent) / window

    def summary(self):
        res = {
            "total_throughput": len(self.exit_times),
            "throughput_recent": self.current_rate(self.exit_times)
        }
        
        for sid, times in self.sink_stats.items():
            res[f"sink_{sid}_total"] = len(times)
            res[f"sink_{sid}_recent"] = self.current_rate(times)
            
        return res