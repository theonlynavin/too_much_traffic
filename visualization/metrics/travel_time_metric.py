from .metric import Metric


class TravelTimeMetric(Metric):
    def __init__(self):
        self.spawn_info = {} # vid -> (time, source_id)
        self.total_time = 0.0
        self.completed = 0
        
        self.source_stats = {} # source_id -> {'total_time': 0.0, 'completed': 0}

    def on_event(self, t, event):
        etype = event["type"]

        if etype == "spawn":
            vid = event["vehicle_id"]
            sid = event["source_id"]
            self.spawn_info[vid] = (t, sid)

        elif etype == "exit":
            vid = event["vehicle_id"]

            if vid in self.spawn_info:
                t0, sid = self.spawn_info[vid]
                dt = t - t0
                self.total_time += dt
                self.completed += 1
                
                if sid not in self.source_stats:
                    self.source_stats[sid] = {'total_time': 0.0, 'completed': 0}
                
                self.source_stats[sid]['total_time'] += dt
                self.source_stats[sid]['completed'] += 1

    def summary(self):
        avg = (
            self.total_time / self.completed
            if self.completed > 0 else 0.0
        )

        res = {
            "completed": self.completed,
            "avg_travel_time": avg
        }
        
        for sid, stats in self.source_stats.items():
            s_avg = stats['total_time'] / stats['completed'] if stats['completed'] > 0 else 0.0
            res[f"source_{sid}_completed"] = stats['completed']
            res[f"source_{sid}_avg_time"] = s_avg
            
        return res