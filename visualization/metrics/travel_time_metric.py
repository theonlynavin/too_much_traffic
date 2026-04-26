from .base import Metric


class TravelTimeMetric(Metric):
    def __init__(self):
        self.spawn_time = {}
        self.total_time = 0.0
        self.completed = 0

    def on_event(self, t, event):
        etype = event["type"]

        if etype == "spawn":
            vid = event["vehicle_id"]
            self.spawn_time[vid] = t

        elif etype == "exit":
            vid = event["vehicle_id"]

            if vid in self.spawn_time:
                dt = t - self.spawn_time[vid]
                self.total_time += dt
                self.completed += 1

    def summary(self):
        avg = (
            self.total_time / self.completed
            if self.completed > 0 else 0.0
        )

        return {
            "completed": self.completed,
            "avg_travel_time": avg
        }