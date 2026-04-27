class RoadLoadTracker:
    def __init__(self, geometry):
        self.geometry = geometry
        self._capacities = {
            rid: road.get("capacity", 0)
            for rid, road in geometry["roads"].items()
        }

    def capacities(self):
        return dict(self._capacities)

    def loads_from_state(self, state, exits=None, t=None):
        loads = {rid: 0 for rid in self.geometry["roads"]}
        for vid, seg in state.items():
            if exits and t is not None:
                if vid in exits and t >= exits[vid]:
                    continue
            rid = seg["road_id"]
            size = seg.get("size", 1)
            loads[rid] = loads.get(rid, 0) + size
        return loads
