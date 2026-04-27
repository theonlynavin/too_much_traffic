"""
Notes:
- High-level utility for capturing the entire simulation state
- Orchestrates to_dict calls across all engine-managed components

TODO:
- Implement full deserialization pipeline (from_dict)
"""
def serialize_system(engine):
    return {
        "time": engine.time,
        "components": {
            cid: {
                "type": comp.__class__.__name__,
                "data": comp.to_dict()
            }
            for cid, comp in engine.components.items()
        },
        "rng": engine.rng.to_dict(),
        "logs": engine.logger.to_dict(),
        "event_queue": engine.queue.to_dict(),
    }