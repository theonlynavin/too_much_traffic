from collections import defaultdict

class StateStore:
    def __init__(self):
        self._state = {}
        self._subscribers = defaultdict(list)

    def get(self, key, default=None):
        return self._state.get(key, default)

    def set(self, engine, key, value):
        old_value = self._state.get(key)
        self._state[key] = value
        
        # Fire hooks (no domain knowledge here)
        for policy_name, hook_method in self._subscribers[key]:
            if policy_name in engine.policies:
                policy = engine.policies[policy_name]
                getattr(policy, hook_method)(engine, key, old_value, value)

    def subscribe(self, key, policy_name, hook_method):
        self._subscribers[key].append((policy_name, hook_method))
