import numpy as np


class EffectsLayer:
    def __init__(self, ax):
        self.spawn_scatter = ax.scatter([], [], s=250, alpha=0.3, zorder=4)
        self.blocked_scatter = ax.scatter(
            [], [], s=140, facecolors='none', edgecolors='red', linewidths=2, zorder=6
        )

    def draw(self, t, state, meta, geometry):
        sx, sy = [], []
        bx, by = [], []

        for vid, seg in state.items():
            road = geometry["roads"][seg["road_id"]]

            if t <= seg["t_end"]:
                alpha = (t - seg["t_start"]) / (seg["t_end"] - seg["t_start"])
            else:
                alpha = 0.98

            from ..geometry import road_to_world
            x, y = road_to_world(road, seg["lane"], alpha)

            # spawn glow
            spawn_t = meta["spawn"].get(vid)
            if spawn_t and (t - spawn_t < 0.5):
                sx.append(x)
                sy.append(y)

            # blocked
            if t > seg["t_end"] and (t - seg["t_end"] > 0.2):
                bx.append(x)
                by.append(y)

        self.spawn_scatter.set_offsets(
            np.column_stack((sx, sy)) if sx else np.empty((0, 2))
        )

        self.blocked_scatter.set_offsets(
            np.column_stack((bx, by)) if bx else np.empty((0, 2))
        )