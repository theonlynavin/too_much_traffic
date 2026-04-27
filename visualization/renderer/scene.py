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
    for pos in geometry["nodes"].values():
        ax.scatter(pos[0], pos[1], s=40, color="black", zorder=3)