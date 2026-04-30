"""
Notes:
- Entry point for the traffic simulation
- Orchestrates engine setup, network building, and visualization

TODO:
- Move manual network setup to a JSON configuration or dedicated factory.
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
from policies.travel_time.free_flow import FreeFlowPolicy
from policies.routing.shortest import ShortestPathRoutingPolicy
from policies.lane.least_loaded import LeastLoadedLanePolicy
from policies.junction.round_robin import RoundRobinJunctionPolicy
from policies.state import TrafficStatePolicy
from policies.transfer import TransferPolicy
from policies.sink.counting import CountingSinkPolicy
from factories.vehicle.random import RandomVehicleFactory
from events.spawn import SpawnEvent
from visualization.timeline import build_geometry
from visualization.recorder import Recorder
from visualization.metrics import default_metrics

def build_engine():
    rng = RNG(seed=42)

    from core.logger import Logger, ConsoleHandler, ColoredFormatter, LogLevel
    logger = Logger(keep_history=True)
    
    # Console logging with colors
    console = ConsoleHandler(level=LogLevel.INFO, formatter=ColoredFormatter())
    logger.add_handler(console)

    engine = Engine(rng, logger)
    return engine


def setup(engine):
    net = Network()

    S1 = Source("S1", junction_id="J1", policy_id="poisson", pos=(-2, -2))
    S2 = Source("S2", junction_id="J5", policy_id="poisson", pos=(-2, -2))
    S3 = Source("S3", junction_id="J8", policy_id="poisson", pos=(2, -2))
    S4 = Source("S4", junction_id="J1", policy_id="poisson", pos=(-2, 2))
    S5 = Source("S5", junction_id="J5", policy_id="poisson", pos=(-2, 2))

    K1 = Sink("K1", junction_id="J12", policy_id="counting", pos=(2, -2))
    K2 = Sink("K2", junction_id="J4", policy_id="counting", pos=(2, -2))
    K3 = Sink("K3", junction_id="J9", policy_id="counting", pos=(-2, -2))
    K4 = Sink("K4", junction_id="J9", policy_id="counting", pos=(-2, 2))
    K5 = Sink("K5", junction_id="J12", policy_id="counting", pos=(2, 2))

    J1 = Junction("J1", incoming=["r_j2_j1"], outgoing=["r_j1_j2"], pos=(0, 0))
    J2 = Junction("J2", incoming=["r_j1_j2", "r_j3_j2", "r_j6_j2"], outgoing=["r_j2_j1", "r_j2_j3", "r_j2_j6"], pos=(20, 0))
    J3 = Junction("J3", incoming=["r_j2_j3", "r_j4_j3", "r_j7_j3"], outgoing=["r_j3_j2", "r_j3_j4", "r_j3_j7"], pos=(40, 0))
    J4 = Junction("J4", incoming=["r_j3_j4"], outgoing=["r_j4_j3"], pos=(60, 0))

    J5 = Junction("J5", incoming=["r_j6_j5"], outgoing=["r_j5_j6"], pos=(0, 20))
    J6 = Junction("J6", incoming=["r_j5_j6", "r_j7_j6", "r_j10_j6"], outgoing=["r_j6_j5", "r_j6_j7", "r_j6_j10"], pos=(20, 20))
    J7 = Junction("J7", incoming=["r_j6_j7", "r_j8_j7", "r_j11_j7"], outgoing=["r_j7_j6", "r_j7_j8", "r_j7_j11"], pos=(40, 20))
    J8 = Junction("J8", incoming=["r_j7_j8"], outgoing=["r_j8_j7"], pos=(60, 20))

    J9 = Junction("J9", incoming=["r_j10_j9"], outgoing=["r_j9_j10"], pos=(0, 40))
    J10 = Junction("J10", incoming=["r_j9_j10", "r_j11_j10", "r_j6_j10"], outgoing=["r_j10_j9", "r_j10_j11", "r_j10_j6"], pos=(20, 40))
    J11 = Junction("J11", incoming=["r_j10_j11", "r_j12_j11", "r_j7_j11"], outgoing=["r_j11_j10", "r_j11_j12", "r_j11_j7"], pos=(40, 40))
    J12 = Junction("J12", incoming=["r_j11_j12"], outgoing=["r_j12_j11"], pos=(60, 40))

    for j in [J1, J2, J3, J4, J5, J6, J7, J8, J9, J10, J11, J12]:
        net.add_junction(j)

    for s in [S1, S2, S3, S4, S5]:
        net.add_source(s)

    for k in [K1, K2, K3, K4, K5]:
        net.add_sink(k)

    roads = [
        Road("r_j1_j2", "J1", "J2", 10, 10, 1),
        Road("r_j2_j1", "J2", "J1", 10, 10, 1),
        Road("r_j2_j3", "J2", "J3", 10, 10, 1),
        Road("r_j3_j2", "J3", "J2", 10, 10, 1),   
        Road("r_j3_j4", "J3", "J4", 10, 10, 1),
        Road("r_j4_j3", "J4", "J3", 10, 10, 1),

        Road("r_j5_j6", "J5", "J6", 10, 10, 1),
        Road("r_j6_j5", "J6", "J5", 10, 10, 1),   
        Road("r_j6_j7", "J6", "J7", 10, 10, 1),
        Road("r_j7_j6", "J7", "J6", 10, 10, 1),
        Road("r_j7_j8", "J7", "J8", 10, 10, 1),
        Road("r_j8_j7", "J8", "J7", 10, 10, 1),

        Road("r_j9_j10", "J9", "J10", 10, 10, 1),
        Road("r_j10_j9", "J10", "J9", 10, 10, 1),
        Road("r_j10_j11", "J10", "J11", 10, 10, 1),
        Road("r_j11_j10", "J11", "J10", 10, 10, 1),
        Road("r_j11_j12", "J11", "J12", 10, 10, 1),
        Road("r_j12_j11", "J12", "J11", 10, 10, 1),

        Road("r_j2_j6", "J2", "J6", 10, 10, 1),
        Road("r_j6_j2", "J6", "J2", 10, 10, 1),
        Road("r_j3_j7", "J3", "J7", 10, 10, 1),
        Road("r_j7_j3", "J7", "J3", 10, 10, 1),

        Road("r_j6_j10", "J6", "J10", 10, 10, 1),
        Road("r_j10_j6", "J10", "J6", 10, 10, 1),
        Road("r_j7_j11", "J7", "J11", 10, 10, 1),
        Road("r_j11_j7", "J11", "J7", 10, 10, 1),
    ]

    for r in roads:
        net.add_road(r)

    net.build(engine)
    engine.set_network(net)

    vehicle_factory = RandomVehicleFactory(
        destinations=["K1", "K2", "K3", "K4", "K5"],
        kinds={
            "car": {"size": 2, "speed": 5.0},
            "truck": {"size": 4, "speed": 3.0},
            "bike": {"size": 1, "speed": 6.0}
        }
    )

    engine.add_policy(
        "poisson",
        PoissonSourcePolicy(rate=2.0, vehicle_factory=vehicle_factory)
    )

    engine.add_policy("routing", ShortestPathRoutingPolicy())
    engine.add_policy("lane", LeastLoadedLanePolicy())
    engine.add_policy("travel_time", FreeFlowPolicy())
    engine.add_policy("junction", RoundRobinJunctionPolicy())
    engine.add_policy("state", TrafficStatePolicy())
    engine.add_policy("transfer", TransferPolicy())
    engine.add_policy("counting", CountingSinkPolicy())

    return net


def seed(engine):
    for sid in engine.network.sources:
        engine.schedule(SpawnEvent(0.0, sid, 0))


def run(engine, network, until=10.0):
    recorder = Recorder()
    recorder.set_geometry(build_geometry(network))
    
    # Attach all standard metrics
    for m in default_metrics():
        recorder.add_metric(m)
    
    engine.add_listener(recorder)
    engine.run(until=until)
    return recorder


def main():
    engine = build_engine()
    engine.logger.log(LogLevel.INFO, src_system(), "main_start")

    network = setup(engine)
    seed(engine)

    recorder = run(engine, network, until=50)
    engine.logger.log(LogLevel.INFO, src_system(), "simulation_done")

    recorder.metrics_manager.pretty_print()
    recorder.metrics_manager.save_to_csv("metrics.csv")
    recorder.metrics_manager.save_to_json("metrics.json")
    recorder.metrics_manager.save_to_txt("metrics.log")
    
    print("Metrics saved to metrics.csv, metrics.json, and metrics.log")

    from visualization.renderer.matplotlib_renderer import MatplotlibRenderer
    renderer = MatplotlibRenderer(timeline=recorder)
    renderer.animate(show_labels=False, save_path="traffic.mp4", show_plot=False)



if __name__ == "__main__":
    main()