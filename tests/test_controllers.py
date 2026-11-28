
import unittest

from controllers.fixed_time import FixedTimeController
from controllers.adaptive import AdaptiveController


class TestTrafficControllers(unittest.TestCase):

    def test_fixed_time(self):

        controller = FixedTimeController()

        self.assertEqual(
            controller.get_signal(0), "NS_GREEN"
        )

        self.assertEqual(
            controller.get_signal(30), "ALL_RED"
        )

        self.assertEqual(
            controller.get_signal(34), "EW_GREEN"
        )

    def test_adaptive_green_times(self):

        controller = AdaptiveController()

        queues = {
            "North": 50,
            "South": 30,
            "East": 10,
            "West": 10
        }

        controller.get_signal(0, queues)

        self.assertEqual(controller.ns_green, 40)
        self.assertEqual(controller.ew_green, 20)

        self.assertEqual(
            controller.get_signal(40, queues),
            "ALL_RED"
        )

        self.assertEqual(
            controller.get_signal(44, queues),
            "EW_GREEN"
        )

    def test_green_time_limits(self):

        controller = AdaptiveController()

        queues = {
            "North": 100,
            "South": 0,
            "East": 0,
            "West": 0
        }

        controller.calculate_green_times(queues)

        self.assertGreaterEqual(
            controller.ew_green, 20
        )

        self.assertEqual(
            controller.ns_green + controller.ew_green,
            60
        )


if __name__ == "__main__":
    unittest.main()
