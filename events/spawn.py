"""
Notes:
- Delegates vehicle creation to source policy
"""
from core.event import Event
from core.logger import LogLevel
from core.log_src import src_event
from events.move import MoveEvent

class SpawnEvent(Event):
    type = "spawn_event"

    def __init__(self, time, source_id, vehicle_id_counter):
        super().__init__(time)
        self.source_id = source_id
        self.vehicle_id_counter = vehicle_id_counter

    def process(self, engine):
        source = engine.components[self.source_id]
        road = engine.components[source.road_id]

        spawn_policy = engine.policies[source.policy_id]

        vehicle = spawn_policy.create_vehicle(
            engine,
            source,
            self.vehicle_id_counter
        )

        vid = vehicle.id

        if road.has_space_for(vehicle.size):
            if "lane" not in engine.policies:
                engine.logger.log(
                    LogLevel.ERROR,
                    src_event(self.type),
                    "lane_policy_missing",
                    available_policies=list(engine.policies.keys())
                )
                raise RuntimeError("Lane policy not set")
            
            lane_policy = engine.policies["lane"]
            lane = lane_policy.choose_lane(engine, road, vehicle)

            road.add_vehicle(vehicle, lane)
            engine.add_component(vehicle)

            engine.logger.log(
                LogLevel.INFO,
                src_event(self.type),
                "vehicle_spawned",
                vehicle_id=vid,
                source_id=source.id,
                road_id=road.id,
                lane=lane,
                size=vehicle.size,
                destination=vehicle.destination,
                cause="arrival"
            )

            time_policy = engine.policies["travel_time"]
            travel_time = time_policy.compute(engine, road, vehicle)

            engine.schedule(
                MoveEvent(
                    engine.time + travel_time,
                    vehicle.id,
                    road.id,
                    lane
                )
            )
        else:
            engine.logger.log(
                LogLevel.WARN,
                src_event(self.type),
                "spawn_dropped",
                vehicle_id=vid,
                source_id=source.id,
                road_id=road.id,
                size=vehicle.size,
                reason="capacity_full"
            )

        dt = spawn_policy.next_interarrival(engine)

        engine.schedule(
            SpawnEvent(
                engine.time + dt,
                self.source_id,
                self.vehicle_id_counter + 1
            )
        )

    def _data_dict(self):
        return {
            "source_id": self.source_id,
            "vehicle_id_counter": self.vehicle_id_counter
        }