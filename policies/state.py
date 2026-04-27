from .base_policy import Policy
from collections import deque

class TrafficStatePolicy(Policy):
    def add_to_lane(self, engine, road_id, lane, vehicle_id, size):
        road = engine.components.get(road_id)
        if road:
            if not (0 <= lane < road.num_lanes):
                raise ValueError(f"invalid lane {lane} for road {road_id}")
            if not self.has_space(engine, road_id, size, road.capacity):
                raise ValueError(f"capacity exceeded on road {road_id}")

        # Update lane queue
        key_lane = f"road:{road_id}:lane:{lane}"
        q = engine.state.get(key_lane, deque())
        q.append(vehicle_id)
        engine.state.set(engine, key_lane, q)

        # Update road load
        key_load = f"road:{road_id}:load"
        load = engine.state.get(key_load, 0)
        engine.state.set(engine, key_load, load + size)

    def remove_from_lane(self, engine, road_id, lane, vehicle_id, size):
        key_lane = f"road:{road_id}:lane:{lane}"
        q = engine.state.get(key_lane, deque())
        if not q or q[0] != vehicle_id:
            raise ValueError(f"Vehicle {vehicle_id} is not at the front of {key_lane}")
        q.popleft()
        engine.state.set(engine, key_lane, q)

        key_load = f"road:{road_id}:load"
        load = engine.state.get(key_load, 0)
        engine.state.set(engine, key_load, load - size)

    def get_lane_size(self, engine, road_id, lane):
        key_lane = f"road:{road_id}:lane:{lane}"
        q = engine.state.get(key_lane, deque())
        return len(q)

    def get_front_vehicle(self, engine, road_id, lane):
        key_lane = f"road:{road_id}:lane:{lane}"
        q = engine.state.get(key_lane, deque())
        return q[0] if q else None
        
    def get_last_vehicle(self, engine, road_id, lane):
        key_lane = f"road:{road_id}:lane:{lane}"
        q = engine.state.get(key_lane, deque())
        return q[-1] if q else None

    def has_space(self, engine, road_id, size, capacity):
        key_load = f"road:{road_id}:load"
        load = engine.state.get(key_load, 0)
        return load + size <= capacity
        
    def get_load(self, engine, road_id):
        key_load = f"road:{road_id}:load"
        return engine.state.get(key_load, 0)
        
    def enqueue_junction(self, engine, junction_id, incoming_rid, vehicle_id, lane):
        junction = engine.components.get(junction_id)
        if junction and incoming_rid not in junction.incoming:
            raise RuntimeError(f"{incoming_rid} not incoming to {junction_id}")

        key = f"junction:{junction_id}:queue:{incoming_rid}"
        q = engine.state.get(key, deque())
        q.append((vehicle_id, lane))
        engine.state.set(engine, key, q)
        
    def peek_junction(self, engine, junction_id, incoming_rid):
        key = f"junction:{junction_id}:queue:{incoming_rid}"
        q = engine.state.get(key, deque())
        return q[0] if q else None
        
    def pop_junction(self, engine, junction_id, incoming_rid):
        key = f"junction:{junction_id}:queue:{incoming_rid}"
        q = engine.state.get(key, deque())
        if not q:
            raise ValueError("empty queue")
        entry = q.popleft()
        engine.state.set(engine, key, q)
        return entry

    def is_waiting_at_junction(self, engine, junction_id, incoming_rid, vehicle_id):
        key = f"junction:{junction_id}:queue:{incoming_rid}"
        q = engine.state.get(key, deque())
        return any(v == vehicle_id for v, _ in q)

    def set_trajectory(self, engine, vehicle_id, trajectory):
        key = f"trajectory:{vehicle_id}"
        engine.state.set(engine, key, trajectory)
        
    def get_trajectory(self, engine, vehicle_id):
        key = f"trajectory:{vehicle_id}"
        return engine.state.get(key, [])
