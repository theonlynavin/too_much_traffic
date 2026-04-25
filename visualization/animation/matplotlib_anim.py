import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


class MatplotlibAnimator:
    def __init__(self, timeline):
        self.timeline = timeline

        self.fig, self.ax = plt.subplots()
        self.ax.set_title("Traffic Simulation")

        self.road_positions = {}
        self.max_len = 0

        self._init_layout()

    # ------------------------

    def _init_layout(self):
        """
        Assign vertical positions to each road/lane
        """
        y = 0
        first_frame = self.timeline.frames[0]["state"]

        for rid, lanes in first_frame["roads"].items():
            self.road_positions[rid] = []

            for lane_id, lane in enumerate(lanes):
                self.road_positions[rid].append(y)
                y += 1

        self.ax.set_ylim(-1, y + 1)

    # ------------------------

    def _extract_points(self, frame):
        xs = []
        ys = []

        state = frame["state"]

        for rid, lanes in state["roads"].items():
            for lane_id, lane in enumerate(lanes):
                y = self.road_positions[rid][lane_id]

                for i, _ in enumerate(lane):
                    xs.append(i)
                    ys.append(y)

                    self.max_len = max(self.max_len, i)

        return xs, ys

    # ------------------------

    def animate(self, interval=200):
        scatter = self.ax.scatter([], [])

        def update(frame_idx):
            frame = self.timeline.frames[frame_idx]

            xs, ys = self._extract_points(frame)

            scatter.set_offsets(list(zip(xs, ys)))

            self.ax.set_xlim(-1, self.max_len + 2)
            self.ax.set_title(f"t = {frame['time']:.2f}")

            return scatter,

        anim = FuncAnimation(
            self.fig,
            update,
            frames=len(self.timeline.frames),
            interval=interval,
            blit=True
        )

        plt.show()