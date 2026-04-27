import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

from .geometry import road_to_world
from .scene import draw_roads, draw_nodes
from .motion import MotionModel
from .road_state import RoadLoadTracker
from .road_overlay import RoadOverlay
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
        self.road_state = RoadLoadTracker(self.geometry)
        self.meta = self._build_meta()

        # static scene
        self._draw_scene()

        # dynamic layers
        self.markers = {"car": "o", "truck": "s", "bus": "D", "motorcycle": "^"}
        self.vehicle_scatters = {}
        for kind, marker in self.markers.items():
            self.vehicle_scatters[kind] = self.ax.scatter([], [], s=80, marker=marker, zorder=5)
        self.vehicle_scatters["default"] = self.ax.scatter([], [], s=80, marker="o", zorder=5)

        self.blocked_scatter = self.ax.scatter(
            [], [], s=140, facecolors='none', edgecolors='red', linewidths=2, zorder=6
        )
        self.vehicle_labels = {}

    # ------------------------

    def _build_meta(self):
        meta = {"dest": {}, "spawn": {}, "exit": {}, "kind": {}}

        for t, e in self.timeline.events:
            if e["type"] == "spawn":
                vid = e["vehicle_id"]
                meta["dest"][vid] = e["destination"]
                meta["spawn"][vid] = t
                meta["kind"][vid] = e.get("kind", "car")

            elif e["type"] == "exit":
                meta["exit"][e["vehicle_id"]] = t

        return meta

    # ------------------------

    def _draw_scene(self):
        self.road_artists = draw_roads(self.ax, self.geometry, self.style)
        draw_nodes(self.ax, self.geometry)
        self.road_overlay = RoadOverlay(
            self.ax,
            self.geometry,
            self.style,
            self.road_artists,
        )

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
            road_loads = self.road_state.loads_from_state(state, self.meta["exit"], t)
            self.road_overlay.update(road_loads)

            grouped_data = {k: {"x": [], "y": [], "c": [], "s": []} for k in self.vehicle_scatters}
            bx, by = [], []
            seen = set()

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

                kind = self.meta["kind"].get(vid, "default")
                if kind not in grouped_data:
                    kind = "default"

                grouped_data[kind]["x"].append(x)
                grouped_data[kind]["y"].append(y)
                grouped_data[kind]["s"].append(size)
                seen.add(vid)

                rgba = plt.cm.colors.to_rgba(base_color)
                grouped_data[kind]["c"].append((rgba[0], rgba[1], rgba[2], alpha_val))

                label = self.vehicle_labels.get(vid)
                if label is None:
                    label = self.ax.text(
                        x + 0.25, y + 0.25, vid,
                        fontsize=6, color='black', zorder=7
                    )
                    self.vehicle_labels[vid] = label
                else:
                    label.set_position((x + 0.25, y + 0.25))
                label.set_visible(True)

            # vehicles
            for k, scatter in self.vehicle_scatters.items():
                g_xs = grouped_data[k]["x"]
                if g_xs:
                    scatter.set_offsets(np.column_stack((g_xs, grouped_data[k]["y"])))
                    scatter.set_sizes(grouped_data[k]["s"])
                    scatter.set_facecolors(grouped_data[k]["c"])
                else:
                    scatter.set_offsets(np.empty((0, 2)))

            # blocked overlay
            self.blocked_scatter.set_offsets(
                np.column_stack((bx, by)) if bx else np.empty((0, 2))
            )

            for vid, label in self.vehicle_labels.items():
                if vid not in seen:
                    label.set_visible(False)

        frames = int(t_max * FRAME_RATE / PLAYBACK_SPEED)

        anim = FuncAnimation(self.fig, update, frames=frames, interval=30)
        anim.save("traffic.mp4", writer="ffmpeg", fps=FRAME_RATE)

        plt.show()