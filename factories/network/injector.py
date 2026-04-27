"""
Notes:
- Injects source and sink nodes into an existing junction network
- Connects sinks with dedicated roads to ensure connectivity in routing tables

TODO:
- FLAG: Active logic (wiring roads/junctions) in a factory/injector.
- FLAG: Missing serialization support.
"""
from components.source import Source
from components.sink import Sink
from components.road import Road


class SourceSinkInjector:
    def __init__(self, n_sources=2, n_sinks=2):
        self.n_sources = n_sources
        self.n_sinks = n_sinks

    def apply(self, net, engine):
        nodes = list(net.junctions.keys())

        if len(nodes) == 0:
            raise ValueError("No junctions in network")

        if self.n_sources + self.n_sinks > len(nodes):
            raise ValueError("Not enough nodes for sources + sinks")

        chosen = engine.rng.sample(nodes, self.n_sources + self.n_sinks)

        sources = chosen[:self.n_sources]
        sinks = chosen[self.n_sources:]

        for i, jid in enumerate(sources):
            j = net.junctions[jid]

            if not j.outgoing:
                continue

            sid = f"S{i}"
            pos = j.pos
            road_id = j.outgoing[0]

            net.add_source(Source(sid, road_id, "poisson", pos))

        for i, jid in enumerate(sinks):
            j = net.junctions[jid]

            kid = f"K{i}"
            pos = j.pos

            net.add_sink(Sink(kid, pos))

            rid = f"R_{jid}_{kid}"
            road = Road(rid, jid, kid, 5, 20, 1)
            net.add_road(road)
            j.outgoing.append(rid)

    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "n_sources": self.n_sources,
            "n_sinks": self.n_sinks
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            n_sources=data["n_sources"],
            n_sinks=data["n_sinks"]
        )
