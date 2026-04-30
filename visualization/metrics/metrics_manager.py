"""
MetricsManager: pure orchestrator.

Responsibilities:
  - Fan engine events to all registered metrics.
  - Build a section-grouped summary from metric.category declarations.
  - Dispatch to any number of reporters.

It knows NOTHING about formatting, file IO, or metric-specific categories.
"""
from collections import defaultdict


class MetricsManager:
    def __init__(self, metrics=None):
        self.metrics = metrics or []

    def add_metric(self, metric):
        self.metrics.append(metric)

    def on_event(self, t, event):
        for m in self.metrics:
            m.on_event(t, event)

    def reset(self):
        for m in self.metrics:
            m.reset()

    def sections(self) -> dict:
        """
        Build a section-grouped summary from all metrics.
        Each metric's `category` attribute determines the section name.
        Returns: dict[section_name, dict[key, value]]
        """
        grouped = defaultdict(dict)
        for m in self.metrics:
            section = getattr(m, "category", "General")
            grouped[section].update(m.summary())
        return dict(grouped)

    def report(self, *reporters):
        """Run one or more reporters against the current metric data."""
        data = self.sections()
        for reporter in reporters:
            reporter.report(data)

    # -------------------------------------------------------------------
    # Convenience shorthands — these do NOT contain formatting logic,
    # they just instantiate the appropriate reporter and delegate.
    # -------------------------------------------------------------------

    def pretty_print(self):
        from .reporters import ConsoleReporter
        self.report(ConsoleReporter())

    def save_to_json(self, path):
        from .reporters import JsonReporter
        self.report(JsonReporter(path))

    def save_to_csv(self, path):
        from .reporters import CsvReporter
        self.report(CsvReporter(path))

    def save_to_txt(self, path):
        from .reporters import TextReporter
        self.report(TextReporter(path))