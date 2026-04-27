"""
System serialization utilities.

TODO:
- Implement full deserialization pipeline
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