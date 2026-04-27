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
            lane_policy = engine.policies.get("lane")
            if lane_policy is None:
                engine.logger.log(
                    LogLevel.ERROR,
                    src_event(self.type),
                    "lane_policy_missing",
                    available_policies=list(engine.policies.keys())
                )
                raise RuntimeError("Lane policy not set")

            lane = lane_policy.choose_lane(engine, road, vehicle)

            time_policy = engine.policies["travel_time"]
            travel_time = time_policy.compute(engine, road, vehicle)

            t0 = engine.time
            t1 = engine.time + travel_time
            vehicle.travel_end_time = t1

            engine.add_component(vehicle)
            road.add_vehicle(vehicle, lane)

            engine.emit({
                "type": "spawn",
                "vehicle_id": vid,
                "source_id": source.id,
                "road_id": road.id,
                "destination": vehicle.destination,
                "lane": lane,
                "kind": vehicle.kind,
                "t_start": t0,
                "t_end": t1
            })

            engine.emit({
                "type": "segment",
                "vehicle_id": vid,
                "road_id": road.id,
                "destination": vehicle.destination,
                "lane": lane,
                "size": vehicle.size,
                "t_start": t0,
                "t_end": t1
            })
            
            engine.logger.log(
                LogLevel.INFO,
                src_event(self.type),
                "vehicle_spawned",
                vehicle_id=vid,
                source_id=source.id,
                road_id=road.id,
                lane=lane,
                kind=vehicle.kind,
                size=vehicle.size,
                destination=vehicle.destination,
                cause="arrival"
            )

            engine.schedule(
                MoveEvent(
                    engine.time + travel_time,
                    vid,
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
                kind=vehicle.kind,
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