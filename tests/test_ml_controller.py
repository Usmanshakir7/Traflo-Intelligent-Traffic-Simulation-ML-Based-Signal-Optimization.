import unittest
from unittest.mock import patch
from controllers.ml_controller import MLController


class FakeModel:
    def predict(self, table):
        return [100, 80, 60, 20, 40]


class TestMLController(unittest.TestCase):
    @patch("controllers.ml_controller.joblib.load")
    def test_model_selects_best_timing(self, fake_load):
        fake_load.return_value = {
            "model": FakeModel(),
            "features": [
                "north_queue", "south_queue", "east_queue", "west_queue",
                "north_interval", "south_interval", "east_interval", "west_interval",
                "ns_green", "ew_green",
            ],
            "green_choices": [20, 25, 30, 35, 40],
            "total_green_time": 60,
        }

        controller = MLController(model_path=__file__)
        queues = {"North": 40, "South": 30, "East": 10, "West": 15}
        self.assertEqual(controller.get_signal(0, queues), "NS_GREEN")
        self.assertEqual((controller.ns_green, controller.ew_green), (35, 25))
        self.assertEqual(controller.get_signal(35, queues), "ALL_RED")
        self.assertEqual(controller.get_signal(39, queues), "EW_GREEN")
        self.assertEqual(controller.get_signal(64, queues), "ALL_RED")
        self.assertEqual(controller.get_signal(68, queues), "NS_GREEN")
        self.assertEqual(len(controller.decision_history), 2)


if __name__ == "__main__":
    unittest.main()
