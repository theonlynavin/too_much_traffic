import numpy as np
import matplotlib.pyplot as plt
from ..geometry import road_to_world


class VehicleLayer:
    def __init__(self, ax, geometry, style):
        self.geometry = geometry
        self.style = style

        self.scatter = ax.scatter([], [], s=80, zorder=5)

    def draw(self, t, state, meta):
        xs, ys, colors, sizes = [], [], [], []

        for vid, seg in state.items():
            road = self.geometry["roads"][seg["road_id"]]

            if t <= seg["t_end"]:
                alpha = (t - seg["t_start"]) / (seg["t_end"] - seg["t_start"])
            else:
                alpha = 0.98

            x, y = road_to_world(road, seg["lane"], alpha)

            dest = meta["dest"].get(vid)
            color = self.style.color(dest)

            # spawn effect
            spawn_t = meta["spawn"].get(vid)
            size = 200 if spawn_t and (t - spawn_t < 0.5) else 80

            xs.append(x)
            ys.append(y)
            colors.append(color)
            sizes.append(size)

        self.scatter.set_offsets(
            np.column_stack((xs, ys)) if xs else np.empty((0, 2))
        )
        self.scatter.set_sizes(sizes)
        self.scatter.set_color(colors)