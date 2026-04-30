import unittest
from core.logger import Logger, LogLevel, ConsoleHandler, LogHandler
from core.log_src import src_system

class MockHandler(LogHandler):
    def __init__(self):
        super().__init__()
        self.emitted = []
    def emit(self, record):
        self.emitted.append(record)

class TestLogger(unittest.TestCase):
    def test_clock_linkage(self):
        class MockClock:
            def __init__(self):
                self.time = 5.0
        
        clock = MockClock()
        logger = Logger()
        logger.set_clock(clock)
        
        logger.log(LogLevel.INFO, src_system(), "test_event")
        self.assertEqual(logger.logs[0]["time"], 5.0)
        
        clock.time = 10.0
        logger.log(LogLevel.INFO, src_system(), "test_event_2")
        self.assertEqual(logger.logs[1]["time"], 10.0)

    def test_keep_history(self):
        logger = Logger(keep_history=False)
        logger.log(LogLevel.INFO, src_system(), "test_event")
        self.assertEqual(len(logger.logs), 0)
        
        logger = Logger(keep_history=True)
        logger.log(LogLevel.INFO, src_system(), "test_event")
        self.assertEqual(len(logger.logs), 1)

    def test_clear_history(self):
        logger = Logger()
        logger.log(LogLevel.INFO, src_system(), "test_event")
        self.assertEqual(len(logger.logs), 1)
        logger.clear_history()
        self.assertEqual(len(logger.logs), 0)

    def test_handlers(self):
        handler = MockHandler()
        logger = Logger()
        logger.add_handler(handler)
        
        logger.log(LogLevel.INFO, src_system(), "test_event")
        self.assertEqual(len(handler.emitted), 1)
        self.assertEqual(handler.emitted[0]["event"], "test_event")

if __name__ == "__main__":
    unittest.main()
