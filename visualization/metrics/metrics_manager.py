import json
import csv

class MetricsManager:
    def __init__(self, metrics):
        self.metrics = metrics

    def on_event(self, t, event):
        for m in self.metrics:
            m.on_event(t, event)

    def summary(self):
        out = {}
        for m in self.metrics:
            out.update(m.summary())
        return out

    def pretty_print(self):
        s = self.summary()
        
        def print_section(title, data):
            if not data:
                return
            print(f"\n--- {title} ---")
            for k, v in sorted(data.items()):
                if isinstance(v, float):
                    print(f"{k:<25}: {v:>8.2f}")
                else:
                    print(f"{k:<25}: {v:>8}")

        print("\n" + "="*40)
        print(" " * 10 + "SIMULATION METRICS SUMMARY")
        print("="*40)

        # Grouping
        totals = {k: v for k, v in s.items() if "sink_" not in k and "source_" not in k and "junction_" not in k}
        junctions = {k: v for k, v in s.items() if "junction_" in k}
        sources = {k: v for k, v in s.items() if "source_" in k}
        sinks = {k: v for k, v in s.items() if "sink_" in k}

        print_section("GENERAL", totals)
        print_section("JUNCTION FLOWS", junctions)
        print_section("SOURCE STATS", sources)
        print_section("SINK STATS", sinks)
        
        print("\n" + "="*40 + "\n")

    def save_to_csv(self, filename):
        s = self.summary()
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Metric", "Value"])
            for k, v in s.items():
                writer.writerow([k, v])

    def save_to_json(self, filename):
        s = self.summary()
        with open(filename, 'w') as f:
            json.dump(s, f, indent=4)

    def save_to_txt(self, filename):
        s = self.summary()
        with open(filename, 'w') as f:
            f.write("="*40 + "\n")
            f.write(" " * 10 + "SIMULATION METRICS SUMMARY\n")
            f.write("="*40 + "\n")
            
            def write_section(title, data):
                if not data:
                    return
                f.write(f"\n--- {title} ---\n")
                for k, v in sorted(data.items()):
                    if isinstance(v, float):
                        f.write(f"{k:<25}: {v:>8.2f}\n")
                    else:
                        f.write(f"{k:<25}: {v:>8}\n")

            totals = {k: v for k, v in s.items() if "sink_" not in k and "source_" not in k and "junction_" not in k}
            junctions = {k: v for k, v in s.items() if "junction_" in k}
            sources = {k: v for k, v in s.items() if "source_" in k}
            sinks = {k: v for k, v in s.items() if "sink_" in k}

            write_section("GENERAL", totals)
            write_section("JUNCTION FLOWS", junctions)
            write_section("SOURCE STATS", sources)
            write_section("SINK STATS", sinks)
            
            f.write("\n" + "="*40 + "\n")