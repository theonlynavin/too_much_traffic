class Timeline:
    def __init__(self):
        self.frames = []

    def add(self, snapshot):
        self.frames.append(snapshot)

class Snapshot:
    def __init__(self, time, roads, vehicles, events):
        self.time = time
        self.roads = roads
        self.vehicles = vehicles
        self.events = events
        
def build_snapshot(engine):
    roads = {}
    vehicles = {}

    for comp in engine.components.values():
        cname = comp.__class__.__name__

        if cname == "Road":
            roads[comp.id] = [list(lane) for lane in comp.lanes]

        elif cname == "Vehicle":
            vehicles[comp.id] = {
                "kind": comp.kind,
                "speed": comp.speed,
                "destination": comp.destination
            }

    return Snapshot(
        time=engine.time,
        roads=roads,
        vehicles=vehicles,
        events=engine.flush_events()
    )