from .base import SinkPolicy
from core.logger import LogLevel
from core.log_src import src_event

class CountingSinkPolicy(SinkPolicy):
    def __init__(self):
        self.received_counts = {} # sink_id -> count
        self.received_ids = {}    # sink_id -> set of vids

    def process_exit(self, engine, sink, vehicle):
        if sink.id not in self.received_counts:
            self.received_counts[sink.id] = 0
            self.received_ids[sink.id] = set()

        if vehicle.id in self.received_ids[sink.id]:
            engine.logger.log(LogLevel.ERROR, "sink_policy", "duplicate_exit", vehicle_id=vehicle.id, sink_id=sink.id)
            raise ValueError(f"Vehicle {vehicle.id} exited twice at {sink.id}")

        self.received_ids[sink.id].add(vehicle.id)
        self.received_counts[sink.id] += 1

        engine.emit({
            "type": "exit",
            "vehicle_id": vehicle.id,
            "sink_id": sink.id
        })
        
        engine.logger.log(
            LogLevel.INFO,
            src_event("move_event"),
            "vehicle_exited_at_sink",
            vehicle_id=vehicle.id,
            sink_id=sink.id,
            total_received=self.received_counts[sink.id]
        )

    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "received_counts": self.received_counts,
            "received_ids": {sid: list(vids) for sid, vids in self.received_ids.items()}
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls()
        obj.received_counts = data.get("received_counts", {})
        obj.received_ids = {sid: set(vids) for sid, vids in data.get("received_ids", {}).items()}
        return obj
