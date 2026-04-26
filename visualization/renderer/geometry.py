import numpy as np

LANE_WIDTH = 1.2

def road_to_world(road, lane, alpha):
    (x1, y1), (x2, y2) = road["start"], road["end"]

    bx = x1 + alpha * (x2 - x1)
    by = y1 + alpha * (y2 - y1)

    dx, dy = x2 - x1, y2 - y1
    norm = np.hypot(dx, dy)
    if norm == 0:
        return bx, by

    px, py = -dy / norm, dx / norm
    offset = (lane - (road["lanes"] - 1) / 2.0) * LANE_WIDTH

    return bx + px * offset, by + py * offset