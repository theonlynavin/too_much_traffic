import unittest
from core.rng import RNG

class TestRNG(unittest.TestCase):
    def test_determinism(self):
        rng1 = RNG(42)
        rng2 = RNG(42)
        
        results1 = [rng1.random() for _ in range(10)]
        results2 = [rng2.random() for _ in range(10)]
        
        self.assertEqual(results1, results2)

    def test_different_seeds(self):
        rng1 = RNG(42)
        rng2 = RNG(43)
        
        results1 = [rng1.random() for _ in range(10)]
        results2 = [rng2.random() for _ in range(10)]
        
        self.assertNotEqual(results1, results2)

if __name__ == "__main__":
    unittest.main()
