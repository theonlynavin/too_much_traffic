"""
Notes:
- Centralized source naming
- All logs must use these helpers
"""
def src_engine():
    return "Engine"

def src_event(event_type: str):
    return f"Event:{event_type}"

def src_component(comp_type: str, cid: str):
    return f"Component:{comp_type}:{cid}"

def src_policy(name: str):
    return f"Policy:{name}"

def src_factory(name: str):
    return f"Factory:{name}"

def src_system():
    return "System"