"""
Notes:
- Renders the static topology (roads and nodes) onto the plot
- Computes lane offsets for multi-lane road visualization

TODO:
- FLAG: Active drawing logic - geometry calculations inside draw_roads.
- Support curvilinear road segments.
"""
import numpy as np

def draw_roads(ax, geometry, style):
    road_artists = {}
    for rid, r in geometry["roads"].items():
        (x1, y1), (x2, y2) = r["start"], r["end"]
        lanes = r["lanes"]

        road_line, = ax.plot(
            [x1, x2], [y1, y2], linewidth=10, color=style.road_base_color, zorder=1
        )
        road_artists[rid] = road_line

        dx, dy = x2 - x1, y2 - y1
        norm = np.hypot(dx, dy)
        if norm == 0:
            continue

        px, py = -dy / norm, dx / norm

        for i in range(1, lanes):
            offset = (i - lanes / 2) * 1.2
            xs = [x1 + px * offset, x2 + px * offset]
            ys = [y1 + py * offset, y2 + py * offset]

            ax.plot(xs, ys, linestyle="--", color="white", linewidth=1, zorder=2)
    return road_artists


def draw_nodes(ax, geometry):
    for nid, node in geometry["nodes"].items():
        pos = node["pos"]
        ntype = node["type"]
        
        if ntype == "junction":
            marker, color, s = "o", "black", 40
        elif ntype == "source":
            marker, color, s = "P", "blue", 80 # Plus sign
        elif ntype == "sink":
            marker, color, s = "X", "red", 80 # Cross
        else:
            marker, color, s = "o", "gray", 40
            
        ax.scatter(pos[0], pos[1], s=s, marker=marker, color=color, zorder=3)
        ax.text(pos[0] + 1, pos[1] + 1, nid, fontsize=8, color=color, fontweight='bold')