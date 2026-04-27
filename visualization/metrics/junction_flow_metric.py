from .metric import Metric


class JunctionFlowMetric(Metric):
    def __init__(self):
        self.junction_counts = {} # junction_id -> count
        self.road_flows = {}     # junction_id -> {from_road: count}

    def on_event(self, t, event):
        if event["type"] == "transfer":
            jid = event["junction_id"]
            from_rid = event["from_road"]
            
            if jid not in self.junction_counts:
                self.junction_counts[jid] = 0
                self.road_flows[jid] = {}
                
            self.junction_counts[jid] += 1
            self.road_flows[jid][from_rid] = self.road_flows[jid].get(from_rid, 0) + 1

    def summary(self):
        res = {}
        # Sort junctions by total flow descending
        sorted_junctions = sorted(self.junction_counts.items(), key=lambda x: x[1], reverse=True)
        
        for jid, total in sorted_junctions:
            res[f"junction_{jid}_total"] = total
            
            # Add detail for incoming roads
            for rid, count in self.road_flows[jid].items():
                res[f"junction_{jid}_from_{rid}"] = count
                
        return res
