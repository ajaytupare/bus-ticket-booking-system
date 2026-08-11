import unittest
import sys
from test_app import BusTicketSystemTestCase

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(BusTicketSystemTestCase)
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
