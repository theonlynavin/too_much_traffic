from .base import Metric


class ThroughputMetric(Metric):
    def __init__(self):
        self.exit_times = []

    def on_event(self, t, event):
        if event["type"] == "exit":
            self.exit_times.append(t)

    def current_rate(self, window=5.0):
        if not self.exit_times:
            return 0.0

        t_now = self.exit_times[-1]
        recent = [t for t in self.exit_times if t_now - t <= window]

        return len(recent) / window

    def summary(self):
        return {
            "throughput_recent": self.current_rate()
        }