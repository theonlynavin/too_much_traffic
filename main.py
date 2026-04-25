"""
Notes:
- Runs simulation
- Captures timeline
- Plays matplotlib animation
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
from policies.routing.fixed import FixedRoutingPolicy
from policies.lane.least_loaded import LeastLoadedLanePolicy

from factories.vehicle.fixed import FixedVehicleFactory

from events.spawn import SpawnEvent

from visualization.timeline import Timeline
from visualization.capture import capture_state
from visualization.animation.matplotlib_anim import MatplotlibAnimator


# ------------------------

def build_engine():
    rng = RNG(seed=42)

    logger = Logger(
        min_level=LogLevel.INFO,   # keep logs quiet for animation
        console_level=LogLevel.INFO,
        file_path=None
    )

    engine = Engine(rng, logger)
    engine.set_event_queue(EventQueue())

    return engine


# ------------------------

def setup(engine):
    net = Network()

    # --- Roads ---
    r1 = Road("r1", start="S", end="J", length=10, capacity=10, num_lanes=2)
    r2 = Road("r2", start="J", end="K", length=10, capacity=2, num_lanes=1)

    net.add_road(r1)
    net.add_road(r2)

    # --- Junction ---
    j = Junction("J", incoming=["r1"], outgoing=["r2"], pos=(12, 10))
    net.add_junction(j)

    # --- Source / Sink ---
    src = Source("S", road_id="r1", policy_id="poisson", pos=(0, 0))
    sink = Sink("K", pos=(12, 20))

    net.add_source(src)
    net.add_sink(sink)

    net.build(engine)
    engine.set_network(net)

    # --- Policies ---
    factory = FixedVehicleFactory(
        size=1,
        destination="K",
        speed=5.0
    )

    engine.add_policy(
        "poisson",
        PoissonSourcePolicy(rate=2.0, vehicle_factory=factory)
    )

    engine.add_policy("routing", FixedRoutingPolicy())
    engine.add_policy("lane", LeastLoadedLanePolicy())
    engine.add_policy("travel_time", CongestionPolicy(alpha=1.0))


# ------------------------

def run_with_timeline(engine, until=30.0):
    timeline = Timeline()

    while not engine.queue.is_empty():
        event = engine.queue.pop()

        if event.time > until:
            break

        engine.time = event.time
        engine.logger.set_time(engine.time)

        event.process(engine)

        # capture AFTER processing event
        state = capture_state(engine)
        timeline.add(engine.time, state)

    return timeline


# ------------------------

def seed(engine):
    engine.schedule(SpawnEvent(0.0, "S", 0))


# ------------------------

def main():
    engine = build_engine()

    engine.logger.log(LogLevel.INFO, src_system(), "main_start")

    setup(engine)
    seed(engine)

    timeline = run_with_timeline(engine, until=30.0)

    engine.logger.log(LogLevel.INFO, src_system(), "simulation_done")

    # --- Animation ---
    animator = MatplotlibAnimator(timeline)
    animator.animate(interval=200)


# ------------------------

if __name__ == "__main__":
    main()