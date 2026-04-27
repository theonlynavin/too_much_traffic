"""
Notes:
- Data structures for storing simulation history and metrics
- build_geometry() converts the live network into a static visualization-friendly format

TODO:
- FLAG: Missing to_dict/from_dict for metrics and event logs.
- Add support for persistence (saving/loading history).
"""
class EventLog:
    def __init__(self):
        self.events = []

    def record(self, time, event):
        self.events.append((time, event))

    def __iter__(self):
        return iter(self.events)
        
class SnapshotStore:
    def __init__(self):
        self.frames = []

    def add(self, snapshot):
        self.frames.append(snapshot)
        
    def __iter__(self):
        return iter(self.frames)
        
class SegmentStore:
    def __init__(self):
        self.segments = []

    def add(self, seg):
        self.segments.append(seg)
        
    def __iter__(self):
        return iter(self.segments)
        
class MetricsCollector:
    def __init__(self):
        self.spawn_times = {}
        self.exit_times = {}

    def on_event(self, time, event):
        t = event["type"]

        if t == "spawn":
            self.spawn_times[event["vehicle_id"]] = time

        elif t == "exit":
            self.exit_times[event["vehicle_id"]] = time

    def summary(self):
        total = len(self.exit_times)
        times = [
            self.exit_times[v] - self.spawn_times[v]
            for v in self.exit_times
        ]
        avg = sum(times)/len(times) if times else 0

        return {
            "completed": total,
            "avg_travel_time": avg
        }
        
def build_geometry(network):
    nodes = {}
    roads = {}

    for jid, j in network.junctions.items():
        nodes[jid] = {"pos": j.pos, "type": "junction"}

    for sid, s in network.sources.items():
        j_pos = network.junctions[s.junction_id].pos
        abs_pos = (j_pos[0] + s.pos[0], j_pos[1] + s.pos[1])
        nodes[sid] = {"pos": abs_pos, "type": "source"}

    for sid, s in network.sinks.items():
        j_pos = network.junctions[s.junction_id].pos
        abs_pos = (j_pos[0] + s.pos[0], j_pos[1] + s.pos[1])
        nodes[sid] = {"pos": abs_pos, "type": "sink"}

    for rid, r in network.roads.items():
        roads[rid] = {
            "start": nodes[r.start]["pos"],
            "end": nodes[r.end]["pos"],
            "lanes": r.num_lanes,
            "capacity": r.capacity,
        }

    return {
        "nodes": nodes,
        "roads": roads
    }