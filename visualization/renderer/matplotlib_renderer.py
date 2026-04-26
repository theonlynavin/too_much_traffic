import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

from .geometry import road_to_world
from .scene import draw_roads, draw_nodes
from .motion import MotionModel
from .style import Style

FRAME_RATE = 30
PLAYBACK_SPEED = 0.5

class MatplotlibRenderer:
    def __init__(self, timeline):
        self.timeline = timeline
        self.geometry = timeline.geometry

        self.fig, self.ax = plt.subplots()

        # core systems
        self.motion = MotionModel(timeline.segments.segments)
        self.style = Style()
        self.meta = self._build_meta()

        # static scene
        self._draw_scene()

        # dynamic layers
        self.vehicle_scatter = self.ax.scatter([], [], s=80, zorder=5)
        self.blocked_scatter = self.ax.scatter(
            [], [], s=140, facecolors='none', edgecolors='red', linewidths=2, zorder=6
        )

    # ------------------------

    def _build_meta(self):
        meta = {"dest": {}, "spawn": {}, "exit": {}}

        for t, e in self.timeline.events:
            if e["type"] == "spawn":
                vid = e["vehicle_id"]
                meta["dest"][vid] = e["destination"]
                meta["spawn"][vid] = t

            elif e["type"] == "exit":
                meta["exit"][e["vehicle_id"]] = t

        return meta

    # ------------------------

    def _draw_scene(self):
        draw_roads(self.ax, self.geometry)
        draw_nodes(self.ax, self.geometry)

        xs = [p[0] for p in self.geometry["nodes"].values()]
        ys = [p[1] for p in self.geometry["nodes"].values()]

        self.ax.set_xlim(min(xs) - 5, max(xs) + 5)
        self.ax.set_ylim(min(ys) - 5, max(ys) + 5)
        self.ax.set_aspect("equal")

    # ------------------------

    def animate(self):
        segments = self.motion.segments
        if not segments:
            print("No segments")
            return

        t_max = max(seg["t_end"] for seg in segments)

        def update(frame):
            t = frame / FRAME_RATE * PLAYBACK_SPEED
            state = self.motion.state_at(t)

            xs, ys = [], []
            colors, sizes = [], []
            bx, by = [], []

            for vid, seg in state.items():
                road = self.geometry["roads"][seg["road_id"]]

                # position
                if t <= seg["t_end"]:
                    alpha = (t - seg["t_start"]) / (seg["t_end"] - seg["t_start"])
                else:
                    alpha = 0.98  # hold near junction

                x, y = road_to_world(road, seg["lane"], alpha)

                # base color
                dest = self.meta["dest"].get(vid)
                base_color = self.style.color(dest)

                # spawn effect
                size = 80
                spawn_t = self.meta["spawn"].get(vid)
                if spawn_t is not None and (t - spawn_t) < 0.5:
                    size = 200

                # exit fade
                alpha_val = 1.0
                exit_t = self.meta["exit"].get(vid)

                if exit_t is not None:
                    dt = t - exit_t
                    if 0 <= dt < 0.5:
                        alpha_val = 1.0 - dt / 0.5
                    elif dt >= 0.5:
                        continue  # remove vehicle

                # blocked detection
                if t > seg["t_end"] and (t - seg["t_end"]) > 0.2:
                    bx.append(x)
                    by.append(y)

                xs.append(x)
                ys.append(y)
                sizes.append(size)

                rgba = plt.cm.colors.to_rgba(base_color)
                colors.append((rgba[0], rgba[1], rgba[2], alpha_val))

            # vehicles
            self.vehicle_scatter.set_offsets(
                np.column_stack((xs, ys)) if xs else np.empty((0, 2))
            )
            self.vehicle_scatter.set_sizes(sizes)
            self.vehicle_scatter.set_facecolors(colors)

            # blocked overlay
            self.blocked_scatter.set_offsets(
                np.column_stack((bx, by)) if bx else np.empty((0, 2))
            )

        frames = int(t_max * FRAME_RATE / PLAYBACK_SPEED)

        anim = FuncAnimation(self.fig, update, frames=frames, interval=30)
        anim.save("traffic.mp4", writer="ffmpeg", fps=FRAME_RATE)

        plt.show()