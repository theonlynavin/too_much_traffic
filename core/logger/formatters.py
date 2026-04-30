import pprint
from .base import LogLevel

# ANSI Colors
COLORS = {
    LogLevel.DEBUG: "\033[36m",    # Cyan
    LogLevel.INFO: "\033[32m",     # Green
    LogLevel.WARN: "\033[33m",     # Yellow
    LogLevel.ERROR: "\033[31m",    # Red
    "RESET": "\033[0m",
    "TIME": "\033[90m",            # Dark Gray
    "SOURCE": "\033[35m",          # Magenta
    "EVENT": "\033[1m"              # Bold
}

class LogFormatter:
    def format(self, record: dict) -> str:
        raise NotImplementedError

class SimpleFormatter(LogFormatter):
    def format(self, record: dict) -> str:
        level = record["level"]
        t = record["time"]
        source = record["source"]
        event = record["event"]
        data = record["data"]
        
        t_str = f"t={t:.3f}" if t is not None else "setup"
        data_str = f" {data}" if data else ""
        return f"[{level}] {t_str} {source}::{event}{data_str}"

class ColoredFormatter(LogFormatter):
    def format(self, record: dict) -> str:
        level_val = getattr(LogLevel, record["level"])
        level_name = record["level"]
        t = record["time"]
        source = record["source"]
        event = record["event"]
        data = record["data"]
        
        c = COLORS.get(level_val, "")
        reset = COLORS["RESET"]
        c_time = COLORS["TIME"]
        c_src = COLORS["SOURCE"]
        c_event = COLORS["EVENT"]
        
        t_str = f"{c_time}t={t:.3f}{reset}" if t is not None else f"{c_time}setup{reset}"
        
        if data:
            if len(data) > 2 or any(isinstance(v, (dict, list)) for v in data.values()):
                data_str = "\n" + pprint.pformat(data, indent=4)
            else:
                data_str = f" {data}"
        else:
            data_str = ""
            
        return f"{c}[{level_name:5}]{reset} {t_str} {c_src}{source}{reset}::{c_event}{event}{reset}{data_str}"
