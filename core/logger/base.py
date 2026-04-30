from enum import IntEnum
from core.log_src import src_system, src_engine

class LogLevel(IntEnum):
    DEBUG = 10
    INFO = 20
    WARN = 30
    ERROR = 40

RESERVED_KEYS = {"level", "time", "source", "event", "data"}

class Logger:
    def __init__(self, keep_history=True):
        self.handlers = []
        self.logs = []
        self.keep_history = keep_history
        self.clock = None
        self._current_time = None

    def add_handler(self, handler):
        self.handlers.append(handler)

    def set_clock(self, clock):
        self.clock = clock

    def set_time(self, t: float):
        self._current_time = t

    def log(self, level: LogLevel, source: str, event: str, **data):
        t = self.clock.time if self.clock is not None else self._current_time

        for key in data:
            if key in RESERVED_KEYS:
                raise ValueError(f"'{key}' is a reserved log field")

        record = {
            "level": level.name,
            "time": t,
            "source": source,
            "event": event,
            "data": data
        }

        if self.keep_history:
            self.logs.append(record)

        for handler in self.handlers:
            handler.emit(record)

    def log_event_scheduled(self, event_type, scheduled_time):
        t = self.clock.time if self.clock is not None else self._current_time
        source = src_system() if t is None else src_engine()
        phase = "setup" if t is None else "runtime"

        self.log(
            LogLevel.DEBUG,
            source,
            "event_scheduled",
            event_type=event_type,
            scheduled_time=scheduled_time,
            phase=phase
        )

    def clear_history(self):
        self.logs.clear()

    def close(self):
        for handler in self.handlers:
            if hasattr(handler, "close"):
                handler.close()

    def to_dict(self):
        return {"logs": self.logs}

    @classmethod
    def from_dict(cls, data):
        obj = cls()
        obj.logs = data.get("logs", [])
        return obj
