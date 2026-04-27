"""
Notes:
- Core logic for vehicle movement and junction transfers
- Handles routing, lane selection, and exit logic
"""
from core.event import Event
from core.logger import LogLevel
from core.log_src import src_event


class MoveEvent(Event):
    type = "move_event"

    def __init__(self, time, vehicle_id, road_id, lane):
        super().__init__(time)
        self.vehicle_id = vehicle_id
        self.road_id = road_id
        self.lane = lane

    def process(self, engine):
        if "transfer" in engine.policies:
            engine.policies["transfer"].process_move(engine, self)
        else:
            engine.logger.log(
                LogLevel.ERROR,
                src_event(self.type),
                "missing_transfer_policy"
            )
            raise RuntimeError("TransferPolicy not found")

    def _data_dict(self):
        return {
            "vehicle_id": self.vehicle_id,
            "road_id": self.road_id,
            "lane": self.lane
        }

    @classmethod
    def from_dict(cls, data):
        d = data["data"]
        return cls(
            time=data["time"],
            vehicle_id=d["vehicle_id"],
            road_id=d["road_id"],
            lane=d["lane"]
        )