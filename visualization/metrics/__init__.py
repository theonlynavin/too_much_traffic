from .metric import Metric
from .metrics_manager import MetricsManager
from .throughput_metric import ThroughputMetric
from .travel_time_metric import TravelTimeMetric
from .junction_flow_metric import JunctionFlowMetric
from .road_load_metric import RoadLoadMetric
from .vehicle_kind_metric import VehicleKindMetric
from .drop_rate_metric import DropRateMetric


def default_metrics():
    """Returns a list of all standard metrics, ready to attach to a Recorder."""
    return [
        ThroughputMetric(),
        TravelTimeMetric(),
        JunctionFlowMetric(),
        RoadLoadMetric(),
        VehicleKindMetric(),
        DropRateMetric(),
    ]
