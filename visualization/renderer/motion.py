class MotionModel:
    def __init__(self, segments):
        self.segments = sorted(segments, key=lambda s: s["t_start"])

    def state_at(self, t):
        latest = {}

        for seg in self.segments:
            vid = seg["vehicle_id"]

            if seg["t_start"] <= t:
                if vid not in latest or seg["t_start"] > latest[vid]["t_start"]:
                    latest[vid] = seg

        return latest