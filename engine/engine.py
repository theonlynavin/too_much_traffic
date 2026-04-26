"""
Notes:
- Only place where time advances

TODO:
- Add step-wise execution mode for debugging
"""
from core.logger import LogLevel
from core.log_src import src_engine, src_system

class Engine:
    def __init__(self, rng, logger):
        self.time = 0.0
        self.queue = None
        self.components = {}
        self.policies = {}
        self.rng = rng
        self.logger = logger
        self.network = None
        self.listeners = []

    def set_event_queue(self, queue):
        self.queue = queue

        self.logger.log(
            LogLevel.INFO,
            src_system(),
            "event_queue_set"
        )
        
    def set_network(self, network):
        self.network = network

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
        if self.queue is None:
            self.logger.log(
                LogLevel.ERROR,
                src_engine(),
                "event_queue_missing"
            )
            raise RuntimeError("Event queue not set")

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

        if self.queue is None:
            self.logger.log(
                LogLevel.ERROR,
                src_engine(),
                "event_queue_missing"
            )
            raise RuntimeError("Event queue not set")

        while not self.queue.is_empty():
            event = self.queue.pop()

            if event.time > until:
                break

            self.time = event.time
            self.logger.set_time(self.time)

            self.logger.log(
                LogLevel.DEBUG,
                src_engine(),
                "event_start",
                event_type=event.type
            )

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