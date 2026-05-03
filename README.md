# Too Much Traffic

A modular and evolving event based traffic simulator.

## Architecture

The simulator is organized into four primary layers:

### 1. Components
Components are passive data structures that represent the physical entities in the simulation. They do not contain logic but store the parameters necessary for simulation:
- **Junction**: Intersection points in the network graph.
- **Road**: Directed edges between junctions, defined by length, capacity, and number of lanes.
- **Source**: Entry points for vehicles, attached to a specific junction with a relative position.
- **Sink**: Exit points for vehicles, attached to a specific junction with a relative position.
- **Vehicle**: Moving entities with specific sizes, speeds, and destinations.

### 2. Events
Events are discrete units of work scheduled on a priority queue ordered by time. The simulation progresses by processing the next available event:
- **SpawnEvent**: Generates a new vehicle at a Source according to a source policy.
- **MoveEvent**: Triggered when a vehicle reaches the end of a trajectory segment. It initiates junction transfer logic or vehicle exit.

### 3. Policies
Policies encapsulate the behavioral logic of the simulation. This modularity allows different simulation rules to be applied without changing the core engine:
- **RoutingPolicy**: Determines the next road for a vehicle (e.g., shortest path using Dijkstra).
- **TravelTimePolicy**: Calculates how long a vehicle takes to traverse a road, accounting for free-flow speed and interactions with vehicles ahead (Head-of-Line blocking).
- **JunctionPolicy**: Manages the order in which vehicles from different incoming roads enter an intersection (e.g., Round Robin).
- **LanePolicy**: Selects which lane a vehicle should occupy upon entering a road.
- **SinkPolicy**: Handles the logic of vehicle exit, such as recording throughput metrics.
Users can define new policies in addition to the existing template policies.

### 4. Engine
The Engine is the central orchestrator. it manages the global simulation clock, hosts the event queue, and maintains the registry of all components and policies.

### 5. Visualization
These contain modules which given a timeline/record of events help in analyzing metrics or convert it to a viewable animation. Metrics can be presented as text, json or csv. Animation is presented as a mp4 file as well as a matplotlib window.

## Simulation Setup

To run a simulation, the user is responsible for defining:
- **Network Topology**: The graph of Junctions and Roads.
- **Sinks, Sources**: The placement of Sources and Sinks.
- **Policy Configuration**: Selecting and registering specific policy implementations with the Engine.
- **Traffic Factories**: Defining the distributions of vehicle types (cars, trucks, etc.) and their destination probabilities.
- **Simulation Parameters**: Setting the simulation duration, random seed, etc.

## Some Existing Policies/Features

- **Multi-Lane Roads**: Support for roads with multiple lanes and lane-selection logic.
- **Dijkstra Routing**: Static shortest-path calculation across the junction graph.
- **Head-of-Line Blocking**: Vehicles realistically slow down and bottleneck based on the motion of the vehicle immediately in front of them.
- **Rendering**: An optimized motion interpolation model and Matplotlib-based renderer for generating MP4 visualization files.

## Future (Ongoing) Development

- **Dynamic Re-routing**: Adjustment of vehicle paths based on live traffic congestion.
- **Non-homogeneous Demand**: Time-varying vehicle arrival rates to simulate peak traffic periods.
- **Full State Serialization**: Mechanisms to save and load the entire simulation state.
