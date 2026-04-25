def capture_state(engine):
    state = {"roads": {}}

    for comp in engine.components.values():
        if comp.__class__.__name__ == "Road":
            state["roads"][comp.id] = [
                list(lane) for lane in comp.lanes
            ]

    return state