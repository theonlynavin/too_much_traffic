import unittest
from engine.event_queue import EventQueue

class MockEvent:
    def __init__(self, time, name):
        self.time = time
        self.name = name
    def to_dict(self):
        return {"time": self.time, "name": self.name}

class TestEventQueue(unittest.TestCase):
    def test_ordering(self):
        eq = EventQueue()
        e1 = MockEvent(10.0, "e1")
        e2 = MockEvent(5.0, "e2")
        e3 = MockEvent(7.5, "e3")
        
        eq.push(e1)
        eq.push(e2)
        eq.push(e3)
        
        self.assertEqual(eq.pop().name, "e2")
        self.assertEqual(eq.pop().name, "e3")
        self.assertEqual(eq.pop().name, "e1")

    def test_deterministic_ordering(self):
        eq = EventQueue()
        e1 = MockEvent(10.0, "e1")
        e2 = MockEvent(10.0, "e2")
        
        eq.push(e1)
        eq.push(e2)
        
        # Should pop in order of push for same timestamp
        self.assertEqual(eq.pop().name, "e1")
        self.assertEqual(eq.pop().name, "e2")

    def test_is_empty(self):
        eq = EventQueue()
        self.assertTrue(eq.is_empty())
        eq.push(MockEvent(1.0, "e1"))
        self.assertFalse(eq.is_empty())
        eq.pop()
        self.assertTrue(eq.is_empty())

if __name__ == "__main__":
    unittest.main()
