import bisect

class MotionModel:
    def __init__(self, segments):
        self.segments = segments
        self.by_vehicle = {}
        for seg in segments:
            vid = seg["vehicle_id"]
            if vid not in self.by_vehicle:
                self.by_vehicle[vid] = []
            self.by_vehicle[vid].append(seg)
            
        for vid in self.by_vehicle:
            self.by_vehicle[vid].sort(key=lambda s: s["t_start"])
            
        self.t_starts = {vid: [s["t_start"] for s in segs] for vid, segs in self.by_vehicle.items()}

    def state_at(self, t):
        latest = {}
        for vid, t_starts in self.t_starts.items():
            idx = bisect.bisect_right(t_starts, t) - 1
            if idx >= 0:
                latest[vid] = self.by_vehicle[vid][idx]
        return latest