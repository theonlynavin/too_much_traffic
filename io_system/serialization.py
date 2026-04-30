from .file_io import save_json, load_json
from core.logger import Logger
from core.rng import RNG
from engine.engine import Engine
from engine.event_queue import EventQueue
from network.network import Network

# Registries for reconstruction
from components.road import Road
from components.junction import Junction
from components.source import Source
from components.sink import Sink
from components.vehicle import Vehicle

COMPONENT_CLASSES = {
    "Road": Road,
    "Junction": Junction,
    "Source": Source,
    "Sink": Sink,
    "Vehicle": Vehicle
}

# Policies will need similar registration
from policies.source.poisson import PoissonSourcePolicy
from policies.travel_time.free_flow import FreeFlowPolicy
from policies.routing.shortest import ShortestPathRoutingPolicy
from policies.lane.least_loaded import LeastLoadedLanePolicy
from policies.junction.round_robin import RoundRobinJunctionPolicy
from policies.state import TrafficStatePolicy
from policies.transfer import TransferPolicy
from policies.sink.counting import CountingSinkPolicy

POLICY_CLASSES = {
    "PoissonSourcePolicy": PoissonSourcePolicy,
    "FreeFlowPolicy": FreeFlowPolicy,
    "ShortestPathRoutingPolicy": ShortestPathRoutingPolicy,
    "LeastLoadedLanePolicy": LeastLoadedLanePolicy,
    "RoundRobinJunctionPolicy": RoundRobinJunctionPolicy,
    "TrafficStatePolicy": TrafficStatePolicy,
    "TransferPolicy": TransferPolicy,
    "CountingSinkPolicy": CountingSinkPolicy
}

from factories.vehicle.random import RandomVehicleFactory

FACTORY_CLASSES = {
    "RandomVehicleFactory": RandomVehicleFactory
}

def deserialize_factory(data):
    cls = FACTORY_CLASSES.get(data["type"])
    if cls:
        return cls.from_dict(data)
    return None

def serialize_system(engine):
    return {
        "time": engine.time,
        "components": {
            cid: {
                "type": comp.__class__.__name__,
                "data": comp.to_dict()
            }
            for cid, comp in engine.components.items()
        },
        "policies": {
            name: {
                "type": pol.__class__.__name__,
                "data": pol.to_dict()
            }
            for name, pol in engine.policies.items()
        },
        "rng": engine.rng.to_dict(),
        "logger": engine.logger.to_dict(),
        "event_queue": engine.queue.to_dict(),
        "network": engine.network.to_dict() if engine.network else None,
        "state": engine.state.to_dict()
    }

def deserialize_system(data):
    # 1. Restore RNG and Logger
    rng = RNG.from_dict(data["rng"])
    logger = Logger.from_dict(data["logger"])
    
    # 2. Create Engine
    engine = Engine(rng, logger)
    engine.time = data["time"]
    
    # 3. Restore Components
    for cid, cdata in data["components"].items():
        cls = COMPONENT_CLASSES.get(cdata["type"])
        if cls:
            comp = cls.from_dict(cdata["data"])
            engine.components[cid] = comp
            
    # 4. Restore Policies
    for name, pdata in data["policies"].items():
        cls = POLICY_CLASSES.get(pdata["type"])
        if cls:
            pol = cls.from_dict(pdata["data"])
            engine.policies[name] = pol
            
    # 5. Restore Event Queue
    engine.queue = EventQueue.from_dict(data["event_queue"])
    
    # 6. Restore Network
    if data["network"]:
        engine.network = Network.from_dict(data["network"])
        
    # 7. Restore StateStore
    from core.state_store import StateStore
    engine.state = StateStore.from_dict(data["state"])
    
    # Re-link logger to engine
    logger.set_clock(engine)
    
    return engine

def save_checkpoint(engine, file_path):
    save_json(serialize_system(engine), file_path)

def load_checkpoint(file_path):
    data = load_json(file_path)
    return deserialize_system(data)