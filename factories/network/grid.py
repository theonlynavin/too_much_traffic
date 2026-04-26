from .base import NetworkFactory
from network.network import Network
from components.junction import Junction
from components.road import Road

class GridNetworkFactory(NetworkFactory):
    def __init__(self, rows, cols, spacing=20):
        self.rows = rows
        self.cols = cols
        self.spacing = spacing

    def build(self, engine):
        net = Network()

        incoming = {}
        outgoing = {}
        pos = {}

        # initialize
        for i in range(self.rows):
            for j in range(self.cols):
                jid = f"J_{i}_{j}"
                pos[jid] = (j * self.spacing, i * self.spacing)
                incoming[jid] = []
                outgoing[jid] = []

        # create roads + adjacency
        for i in range(self.rows):
            for j in range(self.cols):
                if j < self.cols - 1:
                    self._connect(net, incoming, outgoing, i, j, i, j + 1)
                if i < self.rows - 1:
                    self._connect(net, incoming, outgoing, i, j, i + 1, j)

        # NOW create junctions (fully wired)
        for jid in pos:
            net.add_junction(
                Junction(jid, incoming[jid], outgoing[jid], pos[jid])
            )

        return net

    def _connect(self, net, incoming, outgoing, i1, j1, i2, j2):
        a = f"J_{i1}_{j1}"
        b = f"J_{i2}_{j2}"

        r1 = f"R_{a}_{b}"
        r2 = f"R_{b}_{a}"

        net.add_road(Road(r1, a, b, 10, 10, 2))
        net.add_road(Road(r2, b, a, 10, 10, 2))

        outgoing[a].append(r1)
        incoming[b].append(r1)

        outgoing[b].append(r2)
        incoming[a].append(r2)