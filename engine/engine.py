"""
Notes:
- Only place where time advances

TODO:
- Add step-wise execution mode for debugging
"""
from core.logger import LogLevel
from core.log_src import src_engine, src_system
from core.state_store import StateStore
from engine.event_queue import EventQueue

class Engine:
    def __init__(self, rng, logger):
        self.time = 0.0
        self.queue = EventQueue()
        self.components = {}
        self.policies = {}
        self.rng = rng
        self.logger = logger
        self.logger.set_clock(self)
        self.network = None
        self.listeners = []
        self.state = StateStore()

    def set_event_queue(self, queue):
        self.queue = queue

        self.logger.log(
            LogLevel.INFO,
            src_system(),
            "event_queue_set"
        )
        
    def set_network(self, network):
        self.network = network

    def add_listener(self, listener):
        """Register an observer that will receive all emitted events."""
        self.listeners.append(listener)

    def add_component(self, component):
        if component.id in self.components:
            self.logger.log(
                LogLevel.ERROR,
                src_system(),
                "duplicate_component",
                component_id=component.id
            )
            raise ValueError("Duplicate component id")

        self.components[component.id] = component

        self.logger.log(
            LogLevel.INFO,
            src_system(),
            "component_added",
            component_type=component.__class__.__name__,
            component_id=component.id
        )

    def add_policy(self, name, policy):
        if name in self.policies:
            self.logger.log(
                LogLevel.ERROR,
                src_system(),
                "duplicate_policy",
                policy_name=name
            )
            raise ValueError("Duplicate policy name")

        self.policies[name] = policy

        self.logger.log(
            LogLevel.INFO,
            src_system(),
            "policy_added",
            policy_name=name,
            policy_type=policy.__class__.__name__
        )

    def schedule(self, event):

        if event.time < self.time:
            self.logger.log(
                LogLevel.ERROR,
                src_engine(),
                "invalid_schedule",
                event_time=event.time,
                current_time=self.time
            )
            raise ValueError("Cannot schedule event in the past")

        self.queue.push(event)
        self.logger.log_event_scheduled(event.type, event.time)
        
    def emit(self, event: dict):
        for l in self.listeners:
            l.on_event(self.time, event)

    def run(self, until=float("inf")):
        self.logger.log(
            LogLevel.INFO,
            src_system(),
            "simulation_started",
            start_time=self.time,
            until=until
        )

        # Execution loop: time jumps directly to the next event time
        while not self.queue.is_empty():
            event = self.queue.pop()

            # Stop if the next event exceeds the user-defined limit
            if event.time > until:
                break

            # Time advancement happens ONLY here
            self.time = event.time

            self.logger.log(
                LogLevel.DEBUG,
                src_engine(),
                "event_start",
                event_type=event.type
            )

            # Delegate logic to the event object (command pattern)
            try:
                event.process(self)
            except Exception as e:
                self.logger.log(
                    LogLevel.ERROR,
                    src_engine(),
                    "event_failed",
                    event_type=event.type,
                    error=str(e)
                )
                raise

            self.logger.log(
                LogLevel.DEBUG,
                src_engine(),
                "event_end",
                event_type=event.type
            )

        self.logger.log(
            LogLevel.INFO,
            src_system(),
            "simulation_ended",
            end_time=self.time
        )