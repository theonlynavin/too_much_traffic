"""
Reporters handle all output logic for metrics.
MetricsManager knows nothing about formatting — it just calls reporter.report(sections).

A reporter receives:
    sections: dict[str, dict[str, Any]]
        e.g. {"Throughput": {"total_vehicles_exited": 42, ...}, "General": {...}}

To add a new output format, subclass MetricsReporter and implement report().
"""
import json
import csv
from collections import defaultdict


class MetricsReporter:
    """Base reporter interface."""
    def report(self, sections: dict):
        raise NotImplementedError


class ConsoleReporter(MetricsReporter):
    """Pretty-prints metrics to stdout with ANSI colors."""

    def report(self, sections: dict):
        print("\n" + "=" * 55)
        print("\033[1;36m" + " " * 12 + "SIMULATION METRICS REPORT" + "\033[0m")
        print("=" * 55)

        for section_name, data in sections.items():
            if not data:
                continue
            print(f"\n\033[1;34m--- {section_name} ---\033[0m")
            for k, v in sorted(data.items()):
                if isinstance(v, float):
                    print(f"  {k:<35}: \033[32m{v:>10.4f}\033[0m")
                else:
                    print(f"  {k:<35}: \033[32m{v:>10}\033[0m")

        print("\n" + "=" * 55 + "\n")


class JsonReporter(MetricsReporter):
    """Saves metrics as a nested JSON file grouped by section."""

    def __init__(self, file_path):
        self.file_path = file_path

    def report(self, sections: dict):
        with open(self.file_path, "w") as f:
            json.dump(sections, f, indent=4)


class CsvReporter(MetricsReporter):
    """Saves metrics as a flat CSV file with Metric, Section, Value columns."""

    def __init__(self, file_path):
        self.file_path = file_path

    def report(self, sections: dict):
        with open(self.file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Section", "Metric", "Value"])
            for section_name, data in sections.items():
                for k, v in sorted(data.items()):
                    writer.writerow([section_name, k, v])


class TextReporter(MetricsReporter):
    """Saves metrics as a human-readable plain text file."""

    def __init__(self, file_path):
        self.file_path = file_path

    def report(self, sections: dict):
        with open(self.file_path, "w") as f:
            f.write("=" * 55 + "\n")
            f.write(" " * 12 + "SIMULATION METRICS REPORT\n")
            f.write("=" * 55 + "\n")

            for section_name, data in sections.items():
                if not data:
                    continue
                f.write(f"\n--- {section_name} ---\n")
                for k, v in sorted(data.items()):
                    if isinstance(v, float):
                        f.write(f"  {k:<35}: {v:>10.4f}\n")
                    else:
                        f.write(f"  {k:<35}: {v:>10}\n")

            f.write("\n" + "=" * 55 + "\n")
