from ..base_policy import Policy

class SourcePolicy(Policy):

    def next_interarrival(self, engine):
        raise NotImplementedError

    def create_vehicle(self, engine, source, counter):
        raise NotImplementedError