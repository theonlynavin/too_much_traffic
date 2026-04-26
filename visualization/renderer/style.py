class Style:
    def __init__(self):
        self.palette = ["blue", "green", "orange", "purple", "red"]
        self.dest_color = {}

    def color(self, dest):
        if dest not in self.dest_color:
            self.dest_color[dest] = self.palette[len(self.dest_color) % len(self.palette)]
        return self.dest_color[dest]