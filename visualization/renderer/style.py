"""
Notes:
- Centralizes color schemes and styling parameters for the renderer
- Maps destinations to unique colors for vehicle differentiation

TODO:
- FLAG: Hardcoded color palette.
- Support custom themes (dark mode, high contrast).
"""
class Style:
    def __init__(self):
        self.palette = ["blue", "green", "orange", "purple", "red"]
        self.dest_color = {}
        self.road_base_color = "lightgray"
        self.road_jammed_color = "#d62728"
        self.road_text_color = "black"

    def color(self, dest):
        if dest not in self.dest_color:
            self.dest_color[dest] = self.palette[len(self.dest_color) % len(self.palette)]
        return self.dest_color[dest]

    def road_color(self, load, capacity):
        if capacity > 0 and load >= capacity:
            return self.road_jammed_color
        return self.road_base_color

    def road_label_color(self):
        return self.road_text_color