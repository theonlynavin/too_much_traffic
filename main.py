"""
Notes:
- Snapshot-based pipeline
- Engine emits events
- Timeline stores snapshots
- Visualization consumes timeline
"""

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
from policies.travel_time.congestion import CongestionPolicy
from policies.travel_time.free_flow import FreeFlowPolicy
from policies.routing.fixed import FixedRoutingPolicy
from policies.lane.least_loaded import LeastLoadedLanePolicy

from factories.vehicle.fixed import FixedVehicleFactory

from events.spawn import SpawnEvent

from visualization.timeline import Timeline, Snapshot, build_snapshot
from visualization.animation.matplotlib_anim import MatplotlibAnimator


# ------------------------

def build_engine():
    rng = RNG(seed=42)

    logger = Logger(
        min_level=LogLevel.ERROR,
        console_level=LogLevel.INFO,
        file_path=None
    )

    engine = Engine(rng, logger)
    engine.set_event_queue(EventQueue())

    return engine


# ------------------------

def setup(engine):
    net = Network()

    # --- Nodes ---
    src = Source("S", road_id="r1", policy_id="poisson", pos=(0, 0))
    j   = Junction("J", incoming=["r1"], outgoing=["r2"], pos=(20, 0))
    sink = Sink("K", pos=(25, 25))

    net.add_source(src)
    net.add_junction(j)
    net.add_sink(sink)

    # --- Roads ---
    r1 = Road("r1", start="S", end="J", length=10, capacity=10, num_lanes=2)
    r2 = Road("r2", start="J", end="K", length=10, capacity=2, num_lanes=1)

    net.add_road(r1)
    net.add_road(r2)

    # --- Build ---
    net.build(engine)
    engine.set_network(net)

    # --- Policies ---
    factory = FixedVehicleFactory(
        size=1,
        destination="K",
        kind="car",
        speed=5.0
    )

    engine.add_policy(
        "poisson",
        PoissonSourcePolicy(rate=2.0, vehicle_factory=factory)
    )

    engine.add_policy("routing", FixedRoutingPolicy())
    engine.add_policy("lane", LeastLoadedLanePolicy())
    engine.add_policy("travel_time", FreeFlowPolicy())


# ------------------------

def seed(engine):
    engine.schedule(SpawnEvent(0.0, "S", 0))


# ------------------------

def run(engine, until=10.0):
    timeline = Timeline()

    def capture(engine):
        timeline.add(build_snapshot(engine))

    engine.run(until=until, on_event=capture)
    return timeline


# ------------------------

def main():
    engine = build_engine()

    engine.logger.log(LogLevel.INFO, src_system(), "main_start")

    setup(engine)
    seed(engine)

    timeline = run(engine, until=30)

    engine.logger.log(LogLevel.INFO, src_system(), "simulation_done")

    animator = MatplotlibAnimator(timeline, engine.network)
    animator.animate(interval=200)


# ------------------------

if __name__ == "__main__":
    main()