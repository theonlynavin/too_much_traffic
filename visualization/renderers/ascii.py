from .base import Renderer

class ASCIIRenderer(Renderer):
    def render(self, frame):
        print(f"\nt={frame['time']:.3f}")

        for rid, lanes in frame["state"]["roads"].items():
            print(rid)
            for i, lane in enumerate(lanes):
                print(f"  L{i}: {lane}")