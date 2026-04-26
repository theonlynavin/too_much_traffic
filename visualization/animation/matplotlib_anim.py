import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np


STYLE = {
    "car": {"color": "blue", "s": 80},
    "blocked": {
        "color": "blue",
        "edgecolors": "red",
        "linewidths": 2,
        "s": 120,
    },
    "spawn": {"color": "lime", "s": 140},
    "exit": {"color": "gray", "s": 80},
}

ROAD_WIDTH = 20
LANE_WIDTH = 1.2
FRAME_RATE = 30

# Fraction of a slot that is reserved as a visual gap between vehicles.
# 0.15 means vehicles occupy 85% of their slot and the gap is 15%.
SLOT_GAP = 0.15

# How many sim-seconds elapse per wall-second of video.
# Lower = slower playback. Tune to taste.
PLAYBACK_SPEED = 0.5


class MatplotlibAnimator:
    def __init__(self, timeline, network):
        self.timeline = timeline
        self.network = network

        self.fig, self.ax = plt.subplots()
        self.scatters = {}
        self.texts = []
        self.title = None

        self._time = self.timeline.frames[0].time
        self._t_max = self.timeline.frames[-1].time
        self._frame = 0

        self._spawn_flash = {}
        self._exit_fade = {}

        # Persistent set of currently-blocked vehicle IDs.
        # Updated incrementally as events are processed.
        self._blocked: set = set()
        self._processed_events: set = set()

        self._init_plot()

    # ------------------------------------------------------------------ #
    #  Geometry                                                            #
    # ------------------------------------------------------------------ #

    def _normalize(self, x, y):
        n = (x * x + y * y) ** 0.5
        return (0.0, 0.0) if n == 0 else (x / n, y / n)

    def _perp(self, dx, dy):
        return -dy, dx

    def _road_endpoints(self, road):
        return (
            self.network.node_position(road.start),
            self.network.node_position(road.end),
        )

    def _lane_offset_vec(self, road, lane_id):
        """Perpendicular unit vector scaled by lane offset."""
        (x1, y1), (x2, y2) = self._road_endpoints(road)
        px, py = self._normalize(*self._perp(x2 - x1, y2 - y1))
        offset = (lane_id - (road.num_lanes - 1) / 2.0) * LANE_WIDTH
        return px * offset, py * offset

    def _road_to_world(self, road, lane_id, pos_from_start):
        """
        Convert a position (metres from road start) + lane index → world (x, y).
        pos_from_start is clamped to [0, road.length].
        """
        (x1, y1), (x2, y2) = self._road_endpoints(road)

        if road.length == 0:
            return float(x1), float(y1)

        t = np.clip(pos_from_start / road.length, 0.0, 1.0)
        bx = x1 + t * (x2 - x1)
        by = y1 + t * (y2 - y1)

        ox, oy = self._lane_offset_vec(road, lane_id)
        return bx + ox, by + oy

    def _slot_position(self, road, slot_index, num_slots):
        """
        Convert a slot index to a scalar position from road start.

        slot_index 0 = front of queue = closest to road END.
        Slots are evenly spaced with a small gap reserved at each boundary.

        With SLOT_GAP=0.15 and road.length=100, num_slots=4:
          usable = 85.0
          spacing = 21.25
          slot 0 (front) → pos from start = 100 - 0.075*100 - 0*21.25  = 92.5
          slot 3 (back)  → pos from start = 100 - 0.075*100 - 3*21.25  = 29.0
        """
        if num_slots == 0 or road.length == 0:
            return road.length / 2.0

        half_gap = SLOT_GAP / 2.0
        usable = road.length * (1.0 - SLOT_GAP)
        spacing = usable / num_slots if num_slots > 1 else usable

        # Slot 0 is at road.length side (front), slot n-1 is near start
        pos_from_start = road.length * (1.0 - half_gap) - slot_index * spacing
        return np.clip(pos_from_start, 0.0, road.length)

    # ------------------------------------------------------------------ #
    #  Position map from snapshot                                          #
    # ------------------------------------------------------------------ #

    def _extract_positions(self, snapshot):
        """
        Return {vid: (road_id, lane_id, slot_index, num_slots_in_lane, pos_from_start)}.

        Index 0 in the lane list = front of queue = closest to road end.
        """
        pos_map = {}
        for rid, lanes in snapshot.roads.items():
            road = self.network.roads[rid]
            for lane_id, lane in enumerate(lanes):
                n = len(lane)
                for slot_idx, vid in enumerate(lane):
                    pos = self._slot_position(road, slot_idx, n)
                    pos_map[vid] = (rid, lane_id, slot_idx, n, pos)
        return pos_map

    # ------------------------------------------------------------------ #
    #  Junction crossing path                                              #
    # ------------------------------------------------------------------ #

    def _junction_world(self, road0, lane0, road1, lane1):
        """
        Waypoint at the shared node: average the road0-end and road1-start
        world positions so the dot lands on the node circle.
        """
        wx0, wy0 = self._road_to_world(road0, lane0, road0.length)
        wx1, wy1 = self._road_to_world(road1, lane1, 0.0)
        return (wx0 + wx1) / 2.0, (wy0 + wy1) / 2.0

    def _cross_junction_world_pos(self, road0, lane0, p0,
                                   road1, lane1, p1, alpha):
        """
        3-waypoint arc-length path: A → J (junction node) → B.
        Keeps the dot on road geometry even at sharp angles.
        """
        ax_, ay_ = self._road_to_world(road0, lane0, p0)
        jx,  jy  = self._junction_world(road0, lane0, road1, lane1)
        bx,  by  = self._road_to_world(road1, lane1, p1)

        seg1  = np.hypot(jx - ax_, jy - ay_)
        seg2  = np.hypot(bx - jx,  by - jy)
        total = seg1 + seg2 + 1e-9
        t_j   = seg1 / total

        if alpha <= t_j:
            local = alpha / t_j if t_j > 1e-9 else 0.0
            return ax_ + local * (jx - ax_), ay_ + local * (jy - ay_)
        else:
            local = (alpha - t_j) / (1.0 - t_j) if (1.0 - t_j) > 1e-9 else 1.0
            return jx + local * (bx - jx), jy + local * (by - jy)

    # ------------------------------------------------------------------ #
    #  Plot initialisation                                                 #
    # ------------------------------------------------------------------ #

    def _init_plot(self):
        for road in self.network.roads.values():
            (x1, y1), (x2, y2) = self._road_endpoints(road)
            dx, dy = x2 - x1, y2 - y1
            px, py = self._normalize(*self._perp(dx, dy))

            self.ax.plot([x1, x2], [y1, y2],
                         linewidth=ROAD_WIDTH, color="lightgray", zorder=0)

            for i in range(road.num_lanes):
                offset = (i - (road.num_lanes - 1) / 2.0) * LANE_WIDTH
                ox, oy = px * offset, py * offset
                self.ax.plot(
                    [x1 + ox, x2 + ox],
                    [y1 + oy, y2 + oy],
                    linestyle="--", linewidth=1, color="black", zorder=1,
                )

        self._draw_nodes()

        for key, style in STYLE.items():
            self.scatters[key] = self.ax.scatter([], [], **style, zorder=5)

        self.title = self.ax.set_title("")
        self.ax.set_aspect("equal")

        xs, ys = [], []
        for node_dict in [self.network.sources, self.network.sinks,
                          self.network.junctions]:
            for n in node_dict.values():
                xs.append(n.pos[0])
                ys.append(n.pos[1])

        self.ax.set_xlim(min(xs) - 5, max(xs) + 5)
        self.ax.set_ylim(min(ys) - 5, max(ys) + 5)

    def _draw_nodes(self):
        for n in self.network.sources.values():
            self.ax.scatter(*n.pos, color="green", s=200, marker="s", zorder=2)
        for n in self.network.sinks.values():
            self.ax.scatter(*n.pos, color="red", s=200, marker="s", zorder=2)
        for n in self.network.junctions.values():
            self.ax.scatter(*n.pos, color="black", s=140, marker="o", zorder=2)

    # ------------------------------------------------------------------ #
    #  Blocked propagation                                                 #
    # ------------------------------------------------------------------ #

    def _propagate_blocked(self, snapshot, directly_blocked: set) -> set:
        """
        A vehicle is visually blocked if:
          (a) it is directly in the blocked set, OR
          (b) any vehicle ahead of it in the same lane is blocked.

        "Ahead" = lower slot index (closer to road end).
        We iterate each lane front-to-back and latch the blocked flag.
        """
        visually_blocked = set(directly_blocked)

        for rid, lanes in snapshot.roads.items():
            for lane in lanes:
                # lane[0] = front (road end), lane[-1] = back (road start)
                blocked_ahead = False
                for vid in lane:
                    if vid in directly_blocked:
                        blocked_ahead = True
                    if blocked_ahead:
                        visually_blocked.add(vid)

        return visually_blocked

    # ------------------------------------------------------------------ #
    #  Animation                                                           #
    # ------------------------------------------------------------------ #

    def animate(self, interval=16):

        def update(_):
            # ── advance sim clock ──────────────────────────────────────
            self._time += PLAYBACK_SPEED / FRAME_RATE
            self._time = min(self._time, self._t_max)

            # ── advance frame pointer ──────────────────────────────────
            while (
                self._frame < len(self.timeline.frames) - 1
                and self._time >= self.timeline.frames[self._frame + 1].time
            ):
                self._frame += 1

            s0 = self.timeline.frames[self._frame]
            s1 = self.timeline.frames[
                min(self._frame + 1, len(self.timeline.frames) - 1)
            ]

            # ── process events exactly once per snapshot ───────────────
            if self._frame not in self._processed_events:
                self._processed_events.add(self._frame)
                for e in s0.events:
                    vid = e.get("vehicle_id")
                    etype = e["type"]

                    if etype == "blocked":
                        self._blocked.add(vid)

                    elif etype == "unblocked":
                        self._blocked.discard(vid)

                    elif etype == "spawn":
                        self._spawn_flash[vid] = self._time + 0.25

                    elif etype == "exit":
                        self._blocked.discard(vid)
                        # Record exit fade position from pos0 below (after extraction)

            pos0 = self._extract_positions(s0)
            pos1 = self._extract_positions(s1)

            # Now that we have pos0, record exit-fade positions
            # (done here so we have the road data available)
            if self._frame not in self._processed_events or True:
                # Run exit-position registration every frame — deduplicated
                # by checking whether vid is already in _exit_fade.
                for e in s0.events:
                    if e["type"] == "exit":
                        vid = e.get("vehicle_id")
                        if vid not in self._exit_fade and vid in pos0:
                            rid, lid, _, _, p0_ = pos0[vid]
                            road = self.network.roads[rid]
                            x, y = self._road_to_world(road, lid, road.length)
                            self._exit_fade[vid] = (x, y, 6)

            # ── alpha for interpolation ────────────────────────────────
            t0, t1 = s0.time, s1.time
            dt = t1 - t0
            alpha = 1.0 if dt < 1e-9 else np.clip((self._time - t0) / dt, 0.0, 1.0)

            # ── interpolate positions ──────────────────────────────────
            # interp values:
            #   ("road",  road, lane_id, pos_from_start)
            #   ("world", wx, wy)
            interp = {}

            for vid in pos0.keys() | pos1.keys():

                if vid in pos0 and vid in pos1:
                    r0, l0, _, _, p0 = pos0[vid]
                    r1, l1, _, _, p1 = pos1[vid]

                    if r0 == r1 and l0 == l1:
                        # Same lane — lerp scalar position.
                        # Since each event = one slot forward, p1 >= p0
                        # (vehicle moved toward road end or stayed put).
                        # We clamp to prevent visual reversal.
                        p_lerp = p0 + (p1 - p0) * alpha
                        p_lerp = np.clip(p_lerp, min(p0, p1), max(p0, p1))
                        interp[vid] = ("road", self.network.roads[r0], l0, p_lerp)

                    elif r0 == r1 and l0 != l1:
                        # Lane change on same road — lerp position, snap lane at midpoint
                        p_lerp = p0 + (p1 - p0) * alpha
                        lane = l0 if alpha < 0.5 else l1
                        interp[vid] = ("road", self.network.roads[r0], lane, p_lerp)

                    else:
                        # Road transition — arc through junction node
                        road0 = self.network.roads[r0]
                        road1 = self.network.roads[r1]
                        wx, wy = self._cross_junction_world_pos(
                            road0, l0, p0, road1, l1, p1, alpha
                        )
                        interp[vid] = ("world", wx, wy)

                elif vid in pos0:
                    # Vehicle gone by s1 (exited) — hold at last position
                    r0, l0, _, _, p0_ = pos0[vid]
                    interp[vid] = ("road", self.network.roads[r0], l0, p0_)

                else:
                    # Vehicle not yet in s0 (spawning) — grow from road start
                    r1, l1, _, _, p1_ = pos1[vid]
                    interp[vid] = ("road", self.network.roads[r1], l1, p1_ * alpha)

            # ── compute world positions ────────────────────────────────
            positions = {}
            for vid, entry in interp.items():
                if entry[0] == "world":
                    _, wx, wy = entry
                    positions[vid] = (wx, wy)
                else:
                    _, road, lane, pos = entry
                    positions[vid] = self._road_to_world(road, lane, pos)

            # ── blocked propagation ────────────────────────────────────
            visually_blocked = self._propagate_blocked(s0, self._blocked)

            # ── bucket into render styles ──────────────────────────────
            buckets = {k: ([], []) for k in STYLE}

            for vid, (x, y) in positions.items():
                key = "blocked" if vid in visually_blocked else "car"
                buckets[key][0].append(x)
                buckets[key][1].append(y)

            for vid in list(self._spawn_flash):
                if self._time < self._spawn_flash[vid]:
                    if vid in positions:
                        x, y = positions[vid]
                        buckets["spawn"][0].append(x)
                        buckets["spawn"][1].append(y)
                else:
                    del self._spawn_flash[vid]

            for vid in list(self._exit_fade):
                x, y, ttl = self._exit_fade[vid]
                buckets["exit"][0].append(x)
                buckets["exit"][1].append(y)
                ttl -= 1
                if ttl <= 0:
                    del self._exit_fade[vid]
                else:
                    self._exit_fade[vid] = (x, y, ttl)

            # ── update scatter plots ───────────────────────────────────
            for key, scatter in self.scatters.items():
                xs, ys = buckets[key]
                scatter.set_offsets(
                    np.column_stack((xs, ys)) if xs else np.empty((0, 2))
                )

            # ── vehicle labels ─────────────────────────────────────────
            for t in self.texts:
                t.remove()
            self.texts = [
                self.ax.text(x, y, vid, fontsize=6, zorder=6)
                for vid, (x, y) in positions.items()
            ]

            self.title.set_text(f"t = {self._time:.2f}")

        total_frames = int(self._t_max / PLAYBACK_SPEED * FRAME_RATE)

        self.anim = FuncAnimation(
            self.fig,
            update,
            frames=total_frames,
            interval=interval,
            blit=False,
        )

        self.anim.save(
            "traffic.mp4",
            writer="ffmpeg",
            fps=FRAME_RATE,
            bitrate=1000,
            codec="libx264",
            extra_args=["-preset", "ultrafast"],
        )

        plt.show()