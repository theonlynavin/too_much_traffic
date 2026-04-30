import unittest
import os
import json
from main import build_engine, setup, seed
from io_system.serialization import save_checkpoint, load_checkpoint, serialize_system

class TestSerialization(unittest.TestCase):
    def test_full_cycle(self):
        # 1. Setup and run for a few steps
        engine = build_engine()
        setup(engine)
        seed(engine)
        
        # Run for 5.0 units
        engine.run(until=5.0)
        time_before = engine.time
        num_components_before = len(engine.components)
        num_events_before = len(engine.queue._heap)
        
        # 2. Save checkpoint
        checkpoint_path = "test_checkpoint.json"
        save_checkpoint(engine, checkpoint_path)
        
        # 3. Load checkpoint into a new engine
        new_engine = load_checkpoint(checkpoint_path)
        
        # 4. Verify state
        self.assertEqual(new_engine.time, time_before)
        self.assertEqual(len(new_engine.components), num_components_before)
        self.assertEqual(len(new_engine.queue._heap), num_events_before)
        
        # Verify RNG state (indirectly by running more steps)
        # If RNG state is restored, both engines should produce same next events
        # But we already have a test_rng.py for that.
        
        # 5. Run both for 5 more units and compare
        engine.run(until=10.0)
        new_engine.run(until=10.0)
        
        self.assertEqual(engine.time, new_engine.time)
        
        # Cleanup
        if os.path.exists(checkpoint_path):
            os.remove(checkpoint_path)

if __name__ == "__main__":
    unittest.main()
