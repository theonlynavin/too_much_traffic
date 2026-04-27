"""
Notes:
- Defines the physical topology of the simulation
- Computes static routing tables using Dijkstra's algorithm

TODO:
- FLAG: Missing to_dict/from_dict implementation.
- FLAG: Implicit behavior - build() method directly modifies engine state.
- Add graph validation (connectivity, dangling roads)
"""
from core.logger import LogLevel
from core.log_src import src_system
import heapq


class Network:
    def __init__(self):
        self.roads = {}
        self.junctions = {}
        self.sources = {}
        self.sinks = {}
        self.routing_table = {}

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

    def upstream_roads(self, road_id):
        road = self.roads[road_id]
        junction = self.junctions.get(road.start)

        if junction is None:
            return []

        return [self.roads[rid] for rid in junction.incoming]
    
    def next_road(self, current_node, destination):
        key = (current_node, destination)
        rid = self.routing_table.get(key)

        if rid is None:
            return None

        road = self.roads.get(rid)
        if road is None:
            raise RuntimeError(f"Routing table returned invalid road: {rid}")

        if road.start != current_node:
            raise RuntimeError(
                f"Routing inconsistency: {road.start} != {current_node}"
            )

        return rid

    def node_position(self, node_id):
        if node_id in self.junctions:
            return self.junctions[node_id].pos
        if node_id in self.sources:
            return self.sources[node_id].pos
        if node_id in self.sinks:
            return self.sinks[node_id].pos

        raise ValueError(f"Unknown node {node_id}")
    
    def _dijkstra_to(self, destination_id):
        # Dijkstra's algorithm performed in reverse from the destination
        # to find the shortest path from all other nodes to this sink.
        dist = {destination_id: 0.0}
        prev = {}

        heap = [(0.0, destination_id)]

        while heap:
            d, node = heapq.heappop(heap)

            if d > dist[node]:
                continue

            # Explore all incoming roads to current node (moving backwards)
            for road in self._incoming_to_node(node):
                u = road.start
                w = road.length
                nd = d + w

                if u not in dist or nd < dist[u]:
                    dist[u] = nd
                    prev[u] = road.id
                    heapq.heappush(heap, (nd, u))

        return prev
    
    def _incoming_to_node(self, node_id):
        roads = []

        if node_id in self.junctions:
            for rid in self.junctions[node_id].incoming:
                roads.append(self.roads[rid])

        elif node_id in self.sinks:
            for road in self.roads.values():
                if road.end == node_id:
                    roads.append(road)

        return roads

    def build(self, engine):
        for r in self.roads.values():
            engine.add_component(r)

        for j in self.junctions.values():
            engine.add_component(j)

        for s in self.sources.values():
            engine.add_component(s)

        for s in self.sinks.values():
            engine.add_component(s)
            
        self.build_routing_tables() 
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
        
    def build_routing_tables(self):
        self.routing_table = {}

        for sink_id in self.sinks:
            prev = self._dijkstra_to(sink_id)

            for node_id, road_id in prev.items():
                self.routing_table[(node_id, sink_id)] = road_id

    def to_dict(self):
        return {
            "roads": {rid: r.to_dict() for rid, r in self.roads.items()},
            "junctions": {jid: j.to_dict() for jid, j in self.junctions.items()},
            "sources": {sid: s.to_dict() for sid, s in self.sources.items()},
            "sinks": {sid: s.to_dict() for sid, s in self.sinks.items()},
            "routing_table": {f"{k[0]}|{k[1]}": v for k, v in self.routing_table.items()}
        }

    @classmethod
    def from_dict(cls, data):
        from components.road import Road
        from components.junction import Junction
        from components.source import Source
        from components.sink import Sink

        obj = cls()
        obj.roads = {rid: Road.from_dict(d) for rid, d in data["roads"].items()}
        obj.junctions = {jid: Junction.from_dict(d) for jid, d in data["junctions"].items()}
        obj.sources = {sid: Source.from_dict(d) for sid, d in data["sources"].items()}
        obj.sinks = {sid: Sink.from_dict(d) for sid, d in data["sinks"].items()}
        
        rt = {}
        for k, v in data.get("routing_table", {}).items():
            node, dest = k.split("|")
            rt[(node, dest)] = v
        obj.routing_table = rt
        
        return obj
        