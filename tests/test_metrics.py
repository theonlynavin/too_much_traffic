import unittest
from visualization.metrics import (
    ThroughputMetric, TravelTimeMetric, JunctionFlowMetric,
    RoadLoadMetric, VehicleKindMetric, DropRateMetric, MetricsManager, default_metrics
)

def make_spawn(vid, src, dest, kind="car", road="r1", t=0.0):
    return ("spawn", t, {"type": "spawn", "vehicle_id": vid, "source_id": src,
                         "destination": dest, "kind": kind, "road_id": road})

def make_exit(vid, sink, t=5.0):
    return ("exit", t, {"type": "exit", "vehicle_id": vid, "sink_id": sink})

def make_transfer(jid, from_r, to_r, vid, t=2.0):
    return ("transfer", t, {"type": "transfer", "junction_id": jid,
                            "from_road": from_r, "to_road": to_r, "vehicle_id": vid})

def make_dropped(vid, src, reason, kind="car", road="r1"):
    return ("dropped", 0.5, {"type": "dropped", "vehicle_id": vid, "source_id": src,
                              "reason": reason, "kind": kind, "road_id": road})


class TestThroughputMetric(unittest.TestCase):
    def test_counts(self):
        m = ThroughputMetric()
        for evt in [make_spawn("v1", "S0", "K0"), make_spawn("v2", "S0", "K0"),
                    make_exit("v1", "K0"), make_exit("v2", "K0")]:
            m.on_event(evt[1], evt[2])
        s = m.summary()
        self.assertEqual(s["total_vehicles_exited"], 2)
        self.assertEqual(s["total_throughput_rate"], m._rate(m.exit_times))

    def test_reset(self):
        m = ThroughputMetric()
        m.on_event(0.0, make_spawn("v1", "S0", "K0")[2])
        m.reset()
        self.assertEqual(m.summary()["total_vehicles_exited"], 0)


class TestTravelTimeMetric(unittest.TestCase):
    def test_avg_travel_time(self):
        m = TravelTimeMetric()
        m.on_event(0.0, make_spawn("v1", "S0", "K0")[2])
        m.on_event(10.0, make_exit("v1", "K0", t=10.0)[2])
        s = m.summary()
        self.assertEqual(s["vehicle_completed_trips"], 1)
        self.assertAlmostEqual(s["vehicle_avg_travel_time"], 10.0)

    def test_min_max(self):
        m = TravelTimeMetric()
        m.on_event(0.0, make_spawn("v1", "S0", "K0")[2])
        m.on_event(0.0, make_spawn("v2", "S0", "K0")[2])
        m.on_event(5.0, make_exit("v1", "K0", t=5.0)[2])
        m.on_event(15.0, make_exit("v2", "K0", t=15.0)[2])
        s = m.summary()
        self.assertEqual(s["vehicle_min_travel_time"], 5.0)
        self.assertEqual(s["vehicle_max_travel_time"], 15.0)


class TestJunctionFlowMetric(unittest.TestCase):
    def test_counts(self):
        m = JunctionFlowMetric()
        m.on_event(1.0, make_transfer("J1", "r1", "r2", "v1")[2])
        m.on_event(2.0, make_transfer("J1", "r1", "r2", "v2")[2])
        m.on_event(3.0, make_transfer("J2", "r3", "r4", "v3")[2])
        s = m.summary()
        self.assertEqual(s["junction_J1_total"], 2)
        self.assertEqual(s["junction_J2_total"], 1)


class TestDropRateMetric(unittest.TestCase):
    def test_drop_tracking(self):
        m = DropRateMetric()
        m.on_event(0.0, make_spawn("v1", "S0", "K0")[2])
        m.on_event(0.0, make_dropped("v2", "S0", "capacity_full")[2])
        m.on_event(0.0, make_dropped("v3", "S0", "no_path")[2])
        s = m.summary()
        self.assertEqual(s["total_vehicles_spawned"], 1)
        self.assertEqual(s["total_dropped_capacity_full"], 1)
        self.assertEqual(s["total_dropped_no_path"], 1)
        self.assertEqual(s["total_vehicles_attempted"], 3)


class TestVehicleKindMetric(unittest.TestCase):
    def test_kind_breakdown(self):
        m = VehicleKindMetric()
        m.on_event(0.0, {"type": "spawn", "vehicle_id": "v1", "kind": "car",
                         "source_id": "S0", "destination": "K0", "road_id": "r1"})
        m.on_event(5.0, {"type": "exit", "vehicle_id": "v1", "sink_id": "K0"})
        s = m.summary()
        self.assertEqual(s["vehicle_car_spawned"], 1)
        self.assertEqual(s["vehicle_car_exited"], 1)
        self.assertAlmostEqual(s["vehicle_car_avg_travel_time"], 5.0)


class TestMetricsManager(unittest.TestCase):
    def test_fan_out(self):
        mm = MetricsManager()
        t = ThroughputMetric()
        j = JunctionFlowMetric()
        mm.add_metric(t)
        mm.add_metric(j)

        mm.on_event(0.0, make_spawn("v1", "S0", "K0")[2])
        mm.on_event(5.0, make_exit("v1", "K0", t=5.0)[2])
        mm.on_event(1.0, make_transfer("J1", "r1", "r2", "v1")[2])

        s = mm.summary()
        self.assertEqual(s["total_vehicles_exited"], 1)
        self.assertEqual(s["junction_J1_total"], 1)

    def test_default_metrics(self):
        metrics = default_metrics()
        self.assertEqual(len(metrics), 6)


if __name__ == "__main__":
    unittest.main()
