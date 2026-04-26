class Player:
    def __init__(self, timeline, renderer):
        self.timeline = timeline
        self.renderer = renderer

    def play(self):
        for frame in self.timeline.frames:
            self.renderer.render(frame)