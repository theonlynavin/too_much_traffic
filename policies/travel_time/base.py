from ..base_policy import Policy

"""
Notes:
- Defines interface for travel time computation
"""
class TravelTimePolicy(Policy):
    def compute(self, engine, road, vehicle) -> float:
        raise NotImplementedError

    def compute_trajectory(self, engine, road, lane, vehicle, tt_free) -> list:
        state_policy = engine.policies["state"]
        front_vid = state_policy.get_last_vehicle(engine, road.id, lane)
        t_start = engine.time
        
        if not front_vid:
            return [{"t_start": t_start, "t_end": t_start + tt_free, "alpha_start": 0.0, "alpha_end": 1.0}]
            
        front_trajectory = state_policy.get_trajectory(engine, front_vid)
        if not front_trajectory:
            return [{"t_start": t_start, "t_end": t_start + tt_free, "alpha_start": 0.0, "alpha_end": 1.0}]
            
        def x_free(t):
            if t < t_start: return 0.0
            if t > t_start + tt_free: return 1.0
            return (t - t_start) / tt_free

        def x_front(t):
            if not front_trajectory: return 1.0
            if t < front_trajectory[0]["t_start"]: return 0.0
            for seg in front_trajectory:
                if seg["t_start"] <= t <= seg["t_end"]:
                    if seg["t_end"] == seg["t_start"]:
                        return seg["alpha_end"]
                    return seg["alpha_start"] + (t - seg["t_start"]) / (seg["t_end"] - seg["t_start"]) * (seg["alpha_end"] - seg["alpha_start"])
            return 1.0

        T = [t_start, t_start + tt_free]
        for seg in front_trajectory:
            if seg["t_start"] >= t_start: T.append(seg["t_start"])
            if seg["t_end"] >= t_start: T.append(seg["t_end"])

        # Intersections
        for seg in front_trajectory:
            t0 = max(t_start, seg["t_start"])
            t1 = seg["t_end"]
            if t0 >= t1: continue
            
            r_free = 1.0 / tt_free
            r_front = (seg["alpha_end"] - seg["alpha_start"]) / (seg["t_end"] - seg["t_start"])
            
            denom = r_free - r_front
            if abs(denom) > 1e-9:
                t_int = (t_start * r_free + seg["alpha_start"] - seg["t_start"] * r_front) / denom
                if t0 <= t_int <= t1:
                    T.append(t_int)

        T = sorted(list(set([t for t in T if t >= t_start])))
        
        trajectory = []
        for i in range(len(T) - 1):
            t0 = T[i]
            t1 = T[i+1]
            if abs(t1 - t0) < 1e-6: continue
            
            tm = (t0 + t1) / 2
            x_f = x_free(tm)
            x_fr = x_front(tm)
            
            if x_f <= x_fr:
                a0 = x_free(t0)
                a1 = x_free(t1)
            else:
                a0 = x_front(t0)
                a1 = x_front(t1)
                
            a0 = max(0.0, min(1.0, a0))
            a1 = max(0.0, min(1.0, a1))
            
            trajectory.append({
                "t_start": t0,
                "t_end": t1,
                "alpha_start": a0,
                "alpha_end": a1
            })

        merged = []
        for seg in trajectory:
            if not merged:
                merged.append(seg)
            else:
                last = merged[-1]
                r1 = (last["alpha_end"] - last["alpha_start"]) / max(1e-9, last["t_end"] - last["t_start"])
                r2 = (seg["alpha_end"] - seg["alpha_start"]) / max(1e-9, seg["t_end"] - seg["t_start"])
                if abs(r1 - r2) < 1e-6 and abs(last["alpha_end"] - seg["alpha_start"]) < 1e-6:
                    last["t_end"] = seg["t_end"]
                    last["alpha_end"] = seg["alpha_end"]
                else:
                    merged.append(seg)

        if merged:
            merged[-1]["alpha_end"] = 1.0

        return merged