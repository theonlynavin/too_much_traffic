class Timeline:
    def __init__(self):
        self.frames = []

    def add(self, time, state):
        self.frames.append({
            "time": time,
            "state": state
        })