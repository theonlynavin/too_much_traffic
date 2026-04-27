"""
Notes:
- Handles periodic vehicle generation at sources
- Computes initial travel time and schedules first move

TODO:
- FLAG: Missing from_dict implementation.
- Consider moving spawning logic to a dedicated Spawner component.
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
        spawn_policy = engine.policies[source.policy_id]
        vehicle = spawn_policy.create_vehicle(
            engine,
            source,
            self.vehicle_id_counter
        )
        vid = vehicle.id

        # Find initial road from the attached junction
        rid = engine.network.next_road(source.junction_id, vehicle.destination)
        if rid is None:
            engine.logger.log(
                LogLevel.WARN,
                src_event(self.type),
                "spawn_no_path",
                vehicle_id=vid,
                source_id=source.id,
                junction_id=source.junction_id,
                destination=vehicle.destination
            )
            self._schedule_next(engine, spawn_policy)
            return

        road = engine.components[rid]

        state_policy = engine.policies["state"]

        if state_policy.has_space(engine, road.id, vehicle.size, road.capacity):
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
            tt_free = time_policy.compute(engine, road, vehicle)
            trajectory = time_policy.compute_trajectory(engine, road, lane, vehicle, tt_free)

            state_policy.set_trajectory(engine, vid, trajectory)

            engine.add_component(vehicle)
            state_policy.add_to_lane(engine, road.id, lane, vid, vehicle.size)

            t0 = trajectory[0]["t_start"]
            t1 = trajectory[-1]["t_end"]

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

            for seg in trajectory:
                engine.emit({
                    "type": "segment",
                    "vehicle_id": vid,
                    "road_id": road.id,
                    "destination": vehicle.destination,
                    "lane": lane,
                    "size": vehicle.size,
                    "t_start": seg["t_start"],
                    "t_end": seg["t_end"],
                    "alpha_start": seg["alpha_start"],
                    "alpha_end": seg["alpha_end"]
                })
            
            engine.schedule(
                MoveEvent(
                    t1,
                    vid,
                    road.id,
                    lane
                )
            )

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

        self._schedule_next(engine, spawn_policy)

    def _schedule_next(self, engine, spawn_policy):
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

    @classmethod
    def from_dict(cls, data):
        d = data["data"]
        return cls(
            time=data["time"],
            source_id=d["source_id"],
            vehicle_id_counter=d["vehicle_id_counter"]
        )