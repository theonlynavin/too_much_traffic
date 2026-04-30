import json
from .base import LogLevel
from .formatters import SimpleFormatter, LogFormatter

class LogHandler:
    def __init__(self, level: LogLevel = LogLevel.DEBUG, formatter: LogFormatter = None):
        self.level = level
        self.formatter = formatter or SimpleFormatter()

    def emit(self, record: dict):
        raise NotImplementedError

class ConsoleHandler(LogHandler):
    def emit(self, record: dict):
        if getattr(LogLevel, record["level"]) >= self.level:
            print(self.formatter.format(record))

class FileHandler(LogHandler):
    def __init__(self, file_path, level: LogLevel = LogLevel.DEBUG, formatter: LogFormatter = None):
        super().__init__(level, formatter)
        self._file = open(file_path, "w")

    def emit(self, record: dict):
        if getattr(LogLevel, record["level"]) >= self.level:
            line = self.formatter.format(record) if self.formatter else json.dumps(record)
            self._file.write(line + "\n")
            self._file.flush()

    def close(self):
        self._file.close()
