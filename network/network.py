from core.logger import Logger, LogLevel
from core.log_src import src_system

"""
Notes:
- Defines topology and builds engine state
- Does NOT execute simulation

TODO:
- Add graph validation (connectivity, dangling roads)
- Add pathfinding helpers
"""
class Network:
    def __init__(self):
        self.roads = {}
        self.junctions = {}
        self.sources = {}
        self.sinks = {}

    # ------------------------

    def add_road(self, road):
        if road.id in self.roads:
            raise ValueError("Duplicate road id")
        self.roads[road.id] = road

    def add_junction(self, junction):
        if junction.id in self.junctions:
            raise ValueError("Duplicate junction id")
        self.junctions[junction.id] = junction

    def add_source(self, source):
        if source.id in self.sources:
            raise ValueError("Duplicate source id")
        self.sources[source.id] = source

    def add_sink(self, sink):
        if sink.id in self.sinks:
            raise ValueError("Duplicate sink id")
        self.sinks[sink.id] = sink

    # ------------------------
    
    def upstream_roads(self, road_id):
        """
        Returns roads that feed into this road
        """
        road = self.roads[road_id]
        junction = self.junctions.get(road.start)

        if junction is None:
            return []

        return [self.roads[rid] for rid in junction.incoming]

    # ------------------------

    def build(self, engine):
        """
        Registers all components into engine
        """
        for r in self.roads.values():
            engine.add_component(r)

        for j in self.junctions.values():
            engine.add_component(j)

        for s in self.sources.values():
            engine.add_component(s)

        for s in self.sinks.values():
            engine.add_component(s)
        
        engine.set_network(self)
            
        engine.logger.log(
            LogLevel.INFO,
            src_system(),
            "network_built",
            roads=len(self.roads),
            junctions=len(self.junctions),
            sources=len(self.sources),
            sinks=len(self.sinks)
        )