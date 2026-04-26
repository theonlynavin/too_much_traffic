from .base import NetworkFactory
from scipy.spatial import Delaunay
from network.network import Network
from components.junction import Junction
from components.road import Road


class RandomPlanarFactory(NetworkFactory):
    def __init__(self, n_nodes, spread=100):
        self.n_nodes = n_nodes
        self.spread = spread

    def build(self, engine):
        net = Network()

        points = []
        for i in range(self.n_nodes):
            x = engine.rng.uniform(0, self.spread)
            y = engine.rng.uniform(0, self.spread)

            jid = f"J{i}"
            net.add_junction(Junction(jid, [], [], (x, y)))
            points.append((x, y))

        tri = Delaunay(points)

        for simplex in tri.simplices:
            for i in range(3):
                a = f"J{simplex[i]}"
                b = f"J{simplex[(i + 1) % 3]}"

                self._connect(net, a, b)

        return net

    def _connect(self, net, a, b):
        rid = f"R_{a}_{b}"
        if rid in net.roads:
            return

        net.add_road(Road(rid, a, b, 10, 10, 1))
        net.junctions[a].outgoing.append(rid)
        net.junctions[b].incoming.append(rid)