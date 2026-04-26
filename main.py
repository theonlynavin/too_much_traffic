from core.rng import RNG
from core.logger import Logger, LogLevel
from core.log_src import src_system

from engine.engine import Engine
from engine.event_queue import EventQueue
from network.network import Network

from components.road import Road
from components.junction import Junction
from components.source import Source
from components.sink import Sink

from policies.source.poisson import PoissonSourcePolicy
from policies.travel_time.free_flow import FreeFlowPolicy
from policies.routing.shortest import ShortestPathRoutingPolicy
from policies.routing.fixed import FixedRoutingPolicy
from policies.lane.least_loaded import LeastLoadedLanePolicy
from policies.junction.round_robin import RoundRobinJunctionPolicy

from factories.network.random_planar import RandomPlanarFactory
from factories.network.injector import SourceSinkInjector
from factories.vehicle.random import RandomVehicleFactory

from events.spawn import SpawnEvent

from visualization.timeline import build_geometry
from visualization.recorder import Recorder
from visualization.renderer.matplotlib_renderer import MatplotlibRenderer


# ------------------------

def build_engine():
    rng = RNG(seed=42)

    logger = Logger(
        min_level=LogLevel.DEBUG,
        console_level=LogLevel.INFO,
        file_path=None
    )

    engine = Engine(rng, logger)
    engine.set_event_queue(EventQueue())

    return engine


# ------------------------

def setup(engine):
    net = Network()

    # ------------------------
    # Nodes
    # ------------------------

    # Sources
    S0 = Source("S0", road_id="r_s0_j0", policy_id="poisson", pos=(0, 10))
    S1 = Source("S1", road_id="r_s1_j2", policy_id="poisson", pos=(0, -10))
    S2 = Source("S2", road_id="r_s2_j4", policy_id="poisson", pos=(0, 0))

    # Junctions (hex-ish layout)
    J0 = Junction("J0", incoming=["r_s0_j0", "r_j1_j0"], outgoing=["r_j0_j1", "r_j0_j3"], pos=(20, 10))
    J1 = Junction("J1", incoming=["r_j0_j1"], outgoing=["r_j1_j2", "r_j1_j0"], pos=(40, 15))
    J2 = Junction("J2", incoming=["r_s1_j2", "r_j1_j2"], outgoing=["r_j2_j3", "r_j2_j5"], pos=(60, 10))
    J3 = Junction("J3", incoming=["r_j0_j3", "r_j2_j3"], outgoing=["r_j3_j4"], pos=(40, 0))
    J4 = Junction("J4", incoming=["r_s2_j4", "r_j3_j4"], outgoing=["r_j4_j5"], pos=(20, -10))
    J5 = Junction("J5", incoming=["r_j2_j5", "r_j4_j5"], outgoing=["r_j5_k0", "r_j5_k1", "r_j5_k2"], pos=(60, -10))

    # Sinks
    K0 = Sink("K0", pos=(80, -15))
    K1 = Sink("K1", pos=(80, 0))
    K2 = Sink("K2", pos=(80, 15))

    # Add nodes
    for s in [S0, S1, S2]:
        net.add_source(s)

    for j in [J0, J1, J2, J3, J4, J5]:
        net.add_junction(j)

    for k in [K0, K1, K2]:
        net.add_sink(k)

    # ------------------------
    # Roads
    # ------------------------

    roads = [
        # sources → graph
        Road("r_s0_j0", "S0", "J0", 10, 10, 1),
        Road("r_s1_j2", "S1", "J2", 10, 10, 1),
        Road("r_s2_j4", "S2", "J4", 10, 10, 1),

        # internal graph (with loop)
        Road("r_j0_j1", "J0", "J1", 10, 10, 1),
        Road("r_j1_j2", "J1", "J2", 10, 10, 1),
        Road("r_j2_j3", "J2", "J3", 10, 10, 1),
        Road("r_j0_j3", "J0", "J3", 10, 10, 1),  # shortcut

        Road("r_j3_j4", "J3", "J4", 10, 10, 1),
        Road("r_j4_j5", "J4", "J5", 10, 10, 1),
        Road("r_j2_j5", "J2", "J5", 10, 10, 1),

        # feedback loop (to make routing interesting)
        Road("r_j1_j0", "J1", "J0", 10, 10, 1),

        # exits to sinks
        Road("r_j5_k0", "J5", "K0", 10, 10, 1),
        Road("r_j5_k1", "J5", "K1", 10, 10, 1),
        Road("r_j5_k2", "J5", "K2", 10, 10, 1),
    ]

    for r in roads:
        net.add_road(r)

    # ------------------------
    # Build + register
    # ------------------------

    net.build(engine)
    engine.set_network(net)

    # ------------------------
    # Vehicle factory
    # ------------------------

    vehicle_factory = RandomVehicleFactory(
        destinations=["K0", "K1", "K2"],
        kinds={
            "car": {"size": 2, "speed": 5.0},
            "truck": {"size": 4, "speed": 3.0},
            "bike": {"size": 1, "speed": 6.0}
        }
    )

    # ------------------------
    # Policies
    # ------------------------

    engine.add_policy(
        "poisson",
        PoissonSourcePolicy(rate=2.0, vehicle_factory=vehicle_factory)
    )

    engine.add_policy("routing", ShortestPathRoutingPolicy())
    engine.add_policy("lane", LeastLoadedLanePolicy())
    engine.add_policy("travel_time", FreeFlowPolicy())
    engine.add_policy("junction", RoundRobinJunctionPolicy())

    return net

# ------------------------

def seed(engine):
    for sid in engine.network.sources:
        engine.schedule(SpawnEvent(0.0, sid, 0))

# ------------------------

def run(engine, network, until=10.0):
    recorder = Recorder()

    # geometry is static → set once
    recorder.set_geometry(build_geometry(network))

    # hook recorder into engine
    engine.listeners.append(recorder)

    engine.run(until=until)

    return recorder


# ------------------------

def main():
    engine = build_engine()

    engine.logger.log(LogLevel.INFO, src_system(), "main_start")

    network = setup(engine)
    seed(engine)

    recorder = run(engine, network, until=30)

    engine.logger.log(LogLevel.INFO, src_system(), "simulation_done")

    renderer = MatplotlibRenderer(
        timeline=recorder  # contains segments + geometry + metadata
    )
    renderer.animate()


# ------------------------

if __name__ == "__main__":
    main()