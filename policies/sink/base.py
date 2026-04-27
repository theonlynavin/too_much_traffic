from ..base_policy import Policy

class SinkPolicy(Policy):
    def process_exit(self, engine, sink, vehicle):
        raise NotImplementedError
