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