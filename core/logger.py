"""
Notes:
- Engine must set time before logging
- Caller must pass source and event explicitly

TODO:
- Add log rotation for large files
- Add buffered writes / batching
"""
from enum import IntEnum
from core.log_src import src_system, src_engine
import json


class LogLevel(IntEnum):
    DEBUG = 10
    INFO = 20
    WARN = 30
    ERROR = 40


RESERVED_KEYS = {"level", "time", "source", "event", "data"}


class Logger:
    def __init__(self, min_level=LogLevel.DEBUG, console_level=None, file_path=None):
        self.logs = []

        self.min_level = min_level
        self.console_level = console_level

        self._current_time = None
        self._file = open(file_path, "w") if file_path else None

    def set_time(self, t: float):
        self._current_time = t

    def log(self, level: LogLevel, source: str, event: str, **data):
        if level < self.min_level:
            return

        if self._current_time is None:
            # allow only system-level logs before simulation starts
            if source != src_system():
                raise RuntimeError("Logger time not set by engine")
            
        # enforce reserved key safety
        for key in data:
            if key in RESERVED_KEYS:
                raise ValueError(f"'{key}' is a reserved log field")

        record = {
            "level": level.name,
            "time": self._current_time,
            "source": source,
            "event": event,
            "data": data
        }

        # in-memory
        self.logs.append(record)

        # console
        if self.console_level is not None and level >= self.console_level:
            if self._current_time is None:
                print(f"[{level.name}] {source}::{event} {data}")
            else:
                print(f"[{level.name}] t={self._current_time:.3f} {source}::{event} {data}")
                
        # file (JSONL)
        if self._file:
            self._file.write(json.dumps(record) + "\n")
        
    def log_event_scheduled(self, event_type, scheduled_time):
        if self._current_time is None:
            source = src_system()
            phase = "setup"
        else:
            source = src_engine()
            phase = "runtime"

        self.log(
            LogLevel.DEBUG,
            source,
            "event_scheduled",
            event_type=event_type,
            scheduled_time=scheduled_time,
            phase=phase
        )

    def close(self):
        if self._file:
            self._file.close()
            self._file = None
            
    def has_time(self):
        return self._current_time is not None

    def to_dict(self):
        return {"logs": self.logs}

    @classmethod
    def from_dict(cls, data):
        obj = cls()
        obj.logs = data["logs"]
        return obj
    