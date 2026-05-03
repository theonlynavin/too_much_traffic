"""
Notes:
- Animates simulation history using Matplotlib FuncAnimation
- Handles spatial mapping, vehicle styling, and congestion overlays
"""

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
PLAYBACK_SPEED = 1


class MatplotlibRenderer:
    def __init__(self, timeline):
        plt.style.use('ggplot')

        self.timeline = timeline
        self.geometry = timeline.geometry

        self.fig, self.ax = plt.subplots(figsize=(12, 12), dpi=150)

        self.motion = MotionModel(timeline.segments.segments)
        self.style = Style()
        self.road_state = RoadLoadTracker(self.geometry)
        self.meta = self._build_meta()

        self._draw_scene()

        self.markers = {"car": "o", "truck": "s", "bus": "D", "bike": "^"}
        self.vehicle_scatters = {}
        for kind, marker in self.markers.items():
            self.vehicle_scatters[kind] = self.ax.scatter([], [], s=80, marker=marker, zorder=5)
        self.vehicle_scatters["default"] = self.ax.scatter([], [], s=80, marker="o", zorder=5)

        self.blocked_scatter = self.ax.scatter(
            [], [], s=140, facecolors='none', edgecolors='red', linewidths=2, zorder=6
        )

        self.grouped_data = {k: {"x": [], "y": [], "c": [], "s": []} for k in self.vehicle_scatters}

        self.vehicle_labels = {}

    def _build_meta(self):
        meta = {"dest": {}, "spawn": {}, "exit": {}, "kind": {}, "rgba": {}}

        for t, e in self.timeline.events:
            if e["type"] == "spawn":
                vid = e["vehicle_id"]
                meta["dest"][vid] = e["destination"]
                meta["spawn"][vid] = t
                meta["kind"][vid] = e.get("kind", "car")

                base_color = self.style.color(e["destination"])
                meta["rgba"][vid] = plt.cm.colors.to_rgba(base_color)

            elif e["type"] == "exit":
                meta["exit"][e["vehicle_id"]] = t

        return meta

    def _draw_scene(self):
        self.road_artists = draw_roads(self.ax, self.geometry, self.style)
        draw_nodes(self.ax, self.geometry)

        self.road_overlay = RoadOverlay(
            self.ax,
            self.geometry,
            self.style,
            self.road_artists,
        )

        xs = [n["pos"][0] for n in self.geometry["nodes"].values()]
        ys = [n["pos"][1] for n in self.geometry["nodes"].values()]

        self.ax.set_xlim(min(xs) - 10, max(xs) + 10)
        self.ax.set_ylim(min(ys) - 10, max(ys) + 10)
        self.ax.set_aspect("equal")

    def animate(self, show_labels=False, save_path="traffic.mp4", show_plot=True):
        segments = self.motion.segments
        if not segments:
            print("No segments")
            return

        t_max = max(seg["t_end"] for seg in segments)
        frames = int(t_max * FRAME_RATE / PLAYBACK_SPEED)
        times = np.linspace(0, t_max, frames)

        print("Renderer: Precomputing states...")
        timeline_states = [self.motion.state_at(t) for t in times]
        print("Done.")

        def update(frame):
            t = times[frame]
            self.ax.set_title(f"t = {t:.1f} s")

            state = timeline_states[frame]
            road_loads = self.road_state.loads_from_state(state, self.meta["exit"], t)
            self.road_overlay.update(road_loads)

            grouped_data = self.grouped_data
            for g in grouped_data.values():
                g["x"].clear()
                g["y"].clear()
                g["c"].clear()
                g["s"].clear()

            bx, by = [], []
            seen = set()

            # -------- VEHICLES --------
            for vid, seg in state.items():
                road = self.geometry["roads"][seg["road_id"]]

                if t <= seg["t_end"]:
                    a0 = seg.get("alpha_start", 0.0)
                    a1 = seg.get("alpha_end", 1.0)
                    alpha = a0 + (t - seg["t_start"]) / max(1e-9, seg["t_end"] - seg["t_start"]) * (a1 - a0)
                else:
                    alpha = seg.get("alpha_end", 0.98)

                x, y = road_to_world(road, seg["lane"], alpha)

                size = 80
                spawn_t = self.meta["spawn"].get(vid)
                if spawn_t is not None and (t - spawn_t) < 0.5:
                    size = 200

                alpha_val = 1.0
                exit_t = self.meta["exit"].get(vid)
                if exit_t is not None:
                    dt = t - exit_t
                    if 0 <= dt < 0.5:
                        alpha_val = 1.0 - dt / 0.5
                    elif dt >= 0.5:
                        continue

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

                rgba = self.meta["rgba"].get(vid, (0.5, 0.5, 0.5, 1.0))
                grouped_data[kind]["c"].append((rgba[0], rgba[1], rgba[2], alpha_val))

            # -------- DRAW VEHICLES --------
            for k, scatter in self.vehicle_scatters.items():
                g_xs = grouped_data[k]["x"]
                if g_xs:
                    scatter.set_offsets(np.column_stack((g_xs, grouped_data[k]["y"])))
                    scatter.set_sizes(grouped_data[k]["s"])
                    scatter.set_facecolors(grouped_data[k]["c"])
                else:
                    scatter.set_offsets(np.empty((0, 2)))

            self.blocked_scatter.set_offsets(
                np.column_stack((bx, by)) if bx else np.empty((0, 2))
            )

            return list(self.vehicle_scatters.values()) + [self.blocked_scatter]

        frames = int(t_max * FRAME_RATE / PLAYBACK_SPEED)

        anim = FuncAnimation(
            self.fig,
            update,
            frames=frames,
            interval=30,
            blit=True
        )        
        self.ax.invert_yaxis()

        if save_path:
            print(f"Rendering {frames} frames to {save_path}...")
            anim.save(save_path, writer="ffmpeg", fps=FRAME_RATE)
            print("Rendering complete.")

        if show_plot:
            plt.show()