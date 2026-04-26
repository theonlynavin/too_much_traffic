import numpy as np
import matplotlib.pyplot as plt


class DespawnLayer:
    def __init__(self, ax):
        self.scatter = ax.scatter([], [], s=80, zorder=5)

    def draw(self, t, state, meta, geometry):
        xs, ys, colors = [], [], []

        for vid, exit_t in meta["exit"].items():
            dt = t - exit_t
            if 0 <= dt < 0.5:
                # find last segment
                seg = state.get(vid)
                if not seg:
                    continue

                from ..geometry import road_to_world
                road = geometry["roads"][seg["road_id"]]

                x, y = road_to_world(road, seg["lane"], 0.98)

                alpha = 1.0 - dt / 0.5
                colors.append((1, 0, 0, alpha))  # fading red

                xs.append(x)
                ys.append(y)

        self.scatter.set_offsets(
            np.column_stack((xs, ys)) if xs else np.empty((0, 2))
        )
        self.scatter.set_facecolors(colors)