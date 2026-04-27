"""
Notes:
- Listens to engine events and records them for visualization
- Maintains a history of segments and vehicle properties

TODO:
- FLAG: Missing to_dict/from_dict implementation.
"""
from .timeline import EventLog, SegmentStore, MetricsCollector

class Recorder:
    def __init__(self):
        self.events = EventLog()
        self.segments = SegmentStore()

        self.metrics = []

        self.vehicle_dest = {}
        self.spawn_time = {}
        self.geometry = None

    def add_metric(self, metric):
        self.metrics.append(metric)

    def on_event(self, time, event):
        self.events.record(time, event)

        # metrics hook
        for m in self.metrics:
            m.on_event(time, event)

        etype = event.get("type")

        if etype == "segment":
            self.segments.add(event)

        elif etype == "spawn":
            vid = event["vehicle_id"]
            self.vehicle_dest[vid] = event["destination"]
            self.spawn_time[vid] = time

    def set_geometry(self, g):
        self.geometry = g