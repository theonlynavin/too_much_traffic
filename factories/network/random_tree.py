from .base import NetworkFactory
from network.network import Network
from components.junction import Junction
from components.road import Road

class RandomTreeFactory(NetworkFactory):
    def __init__(self, n_nodes, spread=50):
        self.n_nodes = n_nodes
        self.spread = spread

    def build(self, engine):
        net = Network()

        # nodes
        for i in range(self.n_nodes):
            pos = (
                engine.rng.uniform(0, self.spread),
                engine.rng.uniform(0, self.spread)
            )
            net.add_junction(Junction(f"J{i}", [], [], pos))

        nodes = list(net.junctions.keys())

        # connect as tree
        for i in range(1, self.n_nodes):
            parent = engine.rng.choice(nodes[:i])

            self._connect(net, parent, nodes[i])

        return net

    def _connect(self, net, a, b):
        rid = f"R_{a}_{b}"

        net.add_road(Road(rid, a, b, 10, 10, 1))
        net.junctions[a].outgoing.append(rid)
        net.junctions[b].incoming.append(rid)