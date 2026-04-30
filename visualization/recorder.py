"""
The central Recorder is an engine listener that:
  1. Feeds all emitted events into attached metrics (observer pattern).
  2. Stores timeline segments for visualization.

Usage:
    recorder = Recorder()
    recorder.add_metric(ThroughputMetric())
    engine.add_listener(recorder)
    engine.run(until=100)
    recorder.metrics_manager.pretty_print()
"""
from .timeline import EventLog, SegmentStore
from .metrics.metrics_manager import MetricsManager


class Recorder:
    def __init__(self):
        self.events = EventLog()
        self.segments = SegmentStore()
        self.metrics_manager = MetricsManager()
        self._spawn_times = {}   # vid -> t (for cross-metric use)
        self.geometry = None

    def add_metric(self, metric):
        self.metrics_manager.add_metric(metric)

    def on_event(self, time, event):
        # 1. Store the raw event in the timeline
        self.events.record(time, event)

        # 2. Fan out to all metrics
        self.metrics_manager.on_event(time, event)

        # 3. Handle visualization-specific state
        etype = event.get("type")

        if etype == "segment":
            self.segments.add(event)

    def set_geometry(self, g):
        self.geometry = g