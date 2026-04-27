from .base_policy import Policy
from core.logger import LogLevel
from core.log_src import src_event

class TransferPolicy(Policy):
    def process_move(self, engine, event):
        vehicle = engine.components.get(event.vehicle_id)
        if vehicle is None:
            engine.logger.log(
                LogLevel.WARN,
                src_event(event.type),
                "stale_move_event",
                vehicle_id=event.vehicle_id,
                road_id=event.road_id
            )
            return

        road = engine.components.get(event.road_id)
        if road is None:
            engine.logger.log(
                LogLevel.WARN,
                src_event(event.type),
                "stale_move_event_no_road",
                vehicle_id=event.vehicle_id,
                road_id=event.road_id
            )
            return

        state_policy = engine.policies["state"]
        front_vid = state_policy.get_front_vehicle(engine, event.road_id, event.lane)
        
        if front_vid != event.vehicle_id:
            return

        if road.end == vehicle.destination:
            self._exit(engine, vehicle, road, event.lane)
            return

        # Arrive at junction
        junction = engine.components[road.end]
        is_waiting = state_policy.is_waiting_at_junction(engine, junction.id, road.id, vehicle.id)
        
        if not is_waiting:
            state_policy.enqueue_junction(engine, junction.id, road.id, vehicle.id, event.lane)
        
        self._attempt_transfer(engine, junction)

    def _attempt_transfer(self, engine, junction):
        policy = engine.policies["junction"]
        state_policy = engine.policies["state"]

        rid = policy.select_incoming(engine, junction)
        if rid is None:
            return

        entry = state_policy.peek_junction(engine, junction.id, rid)
        if entry is None:
            return

        vid, lane = entry
        vehicle = engine.components.get(vid)
        road = engine.components[rid]

        if vehicle is None:
            state_policy.pop_junction(engine, junction.id, rid)
            return

        front_vid = state_policy.get_front_vehicle(engine, rid, lane)
        if front_vid != vid:
            raise RuntimeError(f"Inconsistent state: vehicle {vid} not at front of {rid}")

        next_road = self._route(engine, vehicle, road, lane)
        if next_road is None:
            return

        if not state_policy.has_space(engine, next_road.id, vehicle.size, next_road.capacity):
            return

        state_policy.pop_junction(engine, junction.id, rid)
        self._move(engine, vehicle, road, next_road, lane)

    def _route(self, engine, vehicle, road, lane):
        routing = engine.policies["routing"]
        state_policy = engine.policies["state"]
        next_road = routing.next_road(engine, vehicle, road)

        if next_road is None:
            state_policy.remove_from_lane(engine, road.id, lane, vehicle.id, vehicle.size)

            engine.emit({
                "type": "dropped",
                "vehicle_id": vehicle.id,
                "road_id": road.id
            })

            engine.logger.log(
                LogLevel.WARN,
                src_event("move_event"),
                "vehicle_dropped_no_path",
                vehicle_id=vehicle.id,
                road_id=road.id,
                destination=vehicle.destination
            )

            return None

        return next_road

    def _move(self, engine, vehicle, road, next_road, lane):
        state_policy = engine.policies["state"]
        state_policy.remove_from_lane(engine, road.id, lane, vehicle.id, vehicle.size)
        self._schedule_new_front(engine, road, lane)
        self._wake_up_upstream_junctions(engine, road)

        lane_policy = engine.policies["lane"]
        new_lane = lane_policy.choose_lane(engine, next_road, vehicle)

        # Segmented trajectory logic
        tt_free = engine.policies["travel_time"].compute(engine, next_road, vehicle)
        trajectory = engine.policies["travel_time"].compute_trajectory(engine, next_road, new_lane, vehicle, tt_free)
        
        state_policy.set_trajectory(engine, vehicle.id, trajectory)
        
        for seg in trajectory:
            engine.emit({
                "type": "segment",
                "vehicle_id": vehicle.id,
                "road_id": next_road.id,
                "lane": new_lane,
                "size": vehicle.size,
                "t_start": seg["t_start"],
                "t_end": seg["t_end"],
                "alpha_start": seg["alpha_start"],
                "alpha_end": seg["alpha_end"]
            })

        state_policy.add_to_lane(engine, next_road.id, new_lane, vehicle.id, vehicle.size)

        from events.move import MoveEvent
        final_t_end = trajectory[-1]["t_end"]
        engine.schedule(MoveEvent(final_t_end, vehicle.id, next_road.id, new_lane))

        engine.logger.log(
            LogLevel.INFO,
            src_event("move_event"),
            "vehicle_routed",
            vehicle_id=vehicle.id,
            from_road=road.id,
            to_road=next_road.id,
            from_lane=lane,
            to_lane=new_lane
        )

    def _exit(self, engine, vehicle, road, lane):
        state_policy = engine.policies["state"]
        state_policy.remove_from_lane(engine, road.id, lane, vehicle.id, vehicle.size)
        self._schedule_new_front(engine, road, lane)
        self._wake_up_upstream_junctions(engine, road)

        sink = engine.components[vehicle.destination]
        prev = sink.received
        sink.record(vehicle.id)

        del engine.components[vehicle.id]

        engine.emit({
            "type": "exit",
            "vehicle_id": vehicle.id,
            "sink_id": sink.id
        })
        
        engine.logger.log(
            LogLevel.INFO,
            src_event("move_event"),
            "vehicle_exited",
            vehicle_id=vehicle.id,
            sink_id=sink.id,
            lane=lane,
            prev_received=prev,
            new_received=sink.received
        )

    def _schedule_new_front(self, engine, road, lane):
        state_policy = engine.policies["state"]
        next_vid = state_policy.get_front_vehicle(engine, road.id, lane)
        if not next_vid:
            return

        trajectory = state_policy.get_trajectory(engine, next_vid)
        if not trajectory:
            return
            
        final_t_end = trajectory[-1]["t_end"]
        if engine.time >= final_t_end:
            from events.move import MoveEvent
            engine.schedule(MoveEvent(engine.time, next_vid, road.id, lane))

    def _wake_up_upstream_junctions(self, engine, road):
        upstream = engine.network.upstream_roads(road.id)
        for r in upstream:
            j = engine.components.get(r.end)
            if j:
                self._attempt_transfer(engine, j)
