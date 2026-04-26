from ..base_policy import Policy


class JunctionPolicy(Policy):
    def select_incoming(self, engine, junction):
        raise NotImplementedError