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
        road = engine.components[self.road_id]

        vehicle = engine.components.get(self.vehicle_id)
        if vehicle is None:
            engine.logger.log(
                LogLevel.WARN,
                src_event(self.type),
                "stale_move_event",
                vehicle_id=self.vehicle_id,
                road_id=self.road_id
            )
            return

        if not road.is_front(self.vehicle_id, self.lane):
            return

        if road.end == vehicle.destination:
            self._exit(engine, vehicle, road)
            return

        junction = engine.components[road.end]
        junction.enqueue(road.id, vehicle.id, self.lane)

        # DO NOT leave it on the road logically
        # (still physically there, but now controlled by junction)

        self._attempt_transfer(engine, junction)

    # ------------------------

    def _attempt_transfer(self, engine, junction):
        policy = engine.policies["junction"]

        rid = policy.select_incoming(engine, junction)
        if rid is None:
            return

        entry = junction.peek(rid)
        if entry is None:
            return

        vid, lane = entry
        vehicle = engine.components.get(vid)
        road = engine.components[rid]

        if vehicle is None:
            junction.pop(rid)
            return

        if not road.is_front(vid, lane):
            raise RuntimeError(
                f"Inconsistent state: vehicle {vid} not at front of {rid}"
            )

        next_road = self._route(engine, vehicle, road)
        if next_road is None:
            return

        if not next_road.has_space_for(vehicle.size):
            return

        junction.pop(rid)
        self._move(engine, vehicle, road, next_road, lane)

    # ------------------------
    def _route(self, engine, vehicle, road):
        routing = engine.policies["routing"]
        next_road = routing.next_road(engine, vehicle, road)

        if next_road is None:
            # drop vehicle
            road.remove_vehicle(vehicle, self.lane)

            engine.emit({
                "type": "dropped",
                "vehicle_id": vehicle.id,
                "road_id": road.id
            })

            engine.logger.log(
                LogLevel.WARN,
                src_event(self.type),
                "vehicle_dropped_no_path",
                vehicle_id=vehicle.id,
                road_id=road.id,
                destination=vehicle.destination
            )

            return None

        return next_road

    # ------------------------

    def _move(self, engine, vehicle, road, next_road, lane):
        road.remove_vehicle(vehicle, lane)

        lane_policy = engine.policies["lane"]
        new_lane = lane_policy.choose_lane(engine, next_road, vehicle)

        tt = engine.policies["travel_time"].compute(engine, next_road, vehicle)

        t0 = engine.time
        t1 = engine.time + tt

        engine.emit({
            "type": "segment",
            "vehicle_id": vehicle.id,
            "road_id": next_road.id,
            "lane": new_lane,
            "t_start": t0,
            "t_end": t1
        })

        next_road.add_vehicle(vehicle, new_lane)

        engine.schedule(
            MoveEvent(engine.time + tt, vehicle.id, next_road.id, new_lane)
        )

        engine.logger.log(
            LogLevel.INFO,
            src_event(self.type),
            "vehicle_routed",
            vehicle_id=vehicle.id,
            from_road=road.id,
            to_road=next_road.id,
            from_lane=lane,
            to_lane=new_lane
        )

    # ------------------------

    def _exit(self, engine, vehicle, road):
        road.remove_vehicle(vehicle, self.lane)

        sink = engine.components[vehicle.destination]
        prev = sink.received
        sink.record(vehicle.id)

        engine.emit({
            "type": "exit",
            "vehicle_id": vehicle.id,
            "sink_id": sink.id
        })
        
        upstream = engine.network.upstream_roads(road.id)

        for r in upstream:
            j = engine.components.get(r.end)
            if j:
                self._attempt_transfer(engine, j)

        engine.logger.log(
            LogLevel.INFO,
            src_event(self.type),
            "vehicle_exited",
            vehicle_id=vehicle.id,
            sink_id=sink.id,
            lane=self.lane,
            prev_received=prev,
            new_received=sink.received
        )

    # ------------------------

    def _data_dict(self):
        return {
            "vehicle_id": self.vehicle_id,
            "road_id": self.road_id,
            "lane": self.lane
        }