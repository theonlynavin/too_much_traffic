from components.source import Source
from components.sink import Sink


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

        # sample without replacement
        chosen = engine.rng.sample(nodes, self.n_sources + self.n_sinks)

        sources = chosen[:self.n_sources]
        sinks = chosen[self.n_sources:]

        # --- sources ---
        for i, jid in enumerate(sources):
            j = net.junctions[jid]

            if not j.outgoing:
                continue  # skip dead node

            sid = f"S{i}"
            pos = j.pos
            road_id = j.outgoing[0]

            net.add_source(Source(sid, road_id, "poisson", pos))

        # --- sinks ---
        for i, jid in enumerate(sinks):
            j = net.junctions[jid]

            kid = f"K{i}"
            pos = j.pos

            net.add_sink(Sink(kid, pos))