import numpy as np


class RoadOverlay:
    def __init__(self, ax, geometry, style, road_artists):
        self.ax = ax
        self.geometry = geometry
        self.style = style
        self.road_artists = road_artists
        self.load_labels = {}

        for rid, road in geometry["roads"].items():
            (x1, y1), (x2, y2) = road["start"], road["end"]
            mx, my = (x1 + x2) / 2.0, (y1 + y2) / 2.0

            dx, dy = x2 - x1, y2 - y1
            norm = np.hypot(dx, dy)
            if norm == 0:
                px, py = 0.0, 0.0
            else:
                px, py = -dy / norm, dx / norm

            label = ax.text(
                mx + px * 1.4,
                my + py * 1.4,
                f"0/{road.get('capacity', 0)}",
                fontsize=7,
                color=self.style.road_label_color(),
                zorder=8,
                ha="center",
                va="center",
            )
            self.load_labels[rid] = label

    def update(self, loads):
        for rid, road in self.geometry["roads"].items():
            cap = road.get("capacity", 0)
            load = loads.get(rid, 0)

            label = self.load_labels[rid]
            label.set_text(f"{load}/{cap}")

            artists = self.road_artists[rid]
            base = artists["base"]
            jam = artists["jam"]

            if cap > 0 and load >= cap:
                jam.set_alpha(1.0)
            else:
                jam.set_alpha(0.0)