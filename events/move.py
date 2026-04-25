"""
Notes:
- Attempts departure from lane
- Local retry only (same lane)

TODO:
- Add upstream retry (network-level)
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
        vehicle = self._get_vehicle(engine)
        road = engine.components[self.road_id]

        if not road.is_front(self.vehicle_id, self.lane):
            return

        if road.end == vehicle.destination:
            self._exit(engine, vehicle, road)
            return

        next_road = self._route(engine, vehicle, road)

        if not next_road.has_space_for(vehicle.size):
            self._log_block(engine, vehicle, road, next_road)
            return

        self._move(engine, vehicle, road, next_road)

    # ------------------------

    def _get_vehicle(self, engine):
        if self.vehicle_id not in engine.components:
            engine.logger.log(
                LogLevel.ERROR,
                src_event(self.type),
                "unknown_vehicle",
                vehicle_id=self.vehicle_id,
                road_id=self.road_id
            )
            raise ValueError("Unknown vehicle")
        return engine.components[self.vehicle_id]

    # ------------------------

    def _route(self, engine, vehicle, road):
        routing = engine.policies["routing"]
        next_road = routing.next_road(engine, vehicle, road)

        if next_road is None:
            engine.logger.log(
                LogLevel.ERROR,
                src_event(self.type),
                "no_route",
                vehicle_id=vehicle.id,
                road_id=road.id
            )
            raise ValueError("No route")

        return next_road

    # ------------------------

    def _exit(self, engine, vehicle, road):
        road.remove_vehicle(vehicle, self.lane)
        self._trigger_next(engine, road)

        sink = engine.components[vehicle.destination]
        prev = sink.received
        sink.record(vehicle.id)

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

    def _move(self, engine, vehicle, road, next_road):
        road.remove_vehicle(vehicle, self.lane)
        self._trigger_next(engine, road)

        lane_policy = engine.policies["lane"]
        new_lane = lane_policy.choose_lane(engine, next_road, vehicle)

        next_road.add_vehicle(vehicle, new_lane)

        tt = engine.policies["travel_time"].compute(engine, next_road, vehicle)

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
            from_lane=self.lane,
            to_lane=new_lane
        )

    # ------------------------

    def _log_block(self, engine, vehicle, road, next_road):
        engine.logger.log(
            LogLevel.WARN,
            src_event(self.type),
            "move_blocked",
            vehicle_id=vehicle.id,
            from_road=road.id,
            to_road=next_road.id,
            lane=self.lane
        )

    # ------------------------

    def _trigger_next(self, engine, road):
        """
        Local + upstream retry
        """
        
        lane_q = road.lanes[self.lane]
        if lane_q:
            engine.schedule(
                MoveEvent(engine.time, lane_q[0], road.id, self.lane)
            )

        network = engine.network
        if network is None:
            engine.logger.log(
                LogLevel.ERROR,
                src_event(self.type),
                "network_missing",
                vehicle_id=self.vehicle_id,
                road_id=self.road_id,
                available_attrs=list(vars(engine).keys())
            )
            raise RuntimeError("Network not set on engine")
        
        upstream = network.upstream_roads(road.id)
        for up_road in upstream:
            for lane_id, q in enumerate(up_road.lanes):
                if not q:
                    continue

                vid = q[0]

                engine.schedule(
                    MoveEvent(engine.time, vid, up_road.id, lane_id)
                )

    # ------------------------

    def _data_dict(self):
        return {
            "vehicle_id": self.vehicle_id,
            "road_id": self.road_id,
            "lane": self.lane
        }