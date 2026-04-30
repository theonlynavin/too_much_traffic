import unittest
from engine.engine import Engine
from engine.event_queue import EventQueue
from core.logger import Logger
from core.rng import RNG

class MockEvent:
    def __init__(self, time):
        self.time = time
        self.type = "mock"
        self.processed = False
    def process(self, engine):
        self.processed = True
    def to_dict(self):
        return {"time": self.time}

class TestEngine(unittest.TestCase):
    def setUp(self):
        self.rng = RNG(42)
        self.logger = Logger()
        self.engine = Engine(self.rng, self.logger)
        self.engine.set_event_queue(EventQueue())

    def test_schedule_and_run(self):
        e1 = MockEvent(1.0)
        e2 = MockEvent(2.0)
        self.engine.schedule(e1)
        self.engine.schedule(e2)
        
        self.engine.run(until=1.5)
        self.assertEqual(self.engine.time, 1.0)
        self.assertTrue(e1.processed)
        self.assertFalse(e2.processed)

    def test_invalid_schedule(self):
        self.engine.time = 10.0
        with self.assertRaises(ValueError):
            self.engine.schedule(MockEvent(5.0))

if __name__ == "__main__":
    unittest.main()
