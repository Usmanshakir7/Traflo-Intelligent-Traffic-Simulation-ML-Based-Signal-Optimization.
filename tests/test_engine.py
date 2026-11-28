
import unittest
from unittest.mock import patch

from core.engine import TrafficSimulation
from controllers.fixed_time import FixedTimeController


class TestSimulationEngine(unittest.TestCase):

    def make_simulation(self):
        return TrafficSimulation(
            FixedTimeController()
        )

    def test_vehicle_accounting(self):

        simulation = self.make_simulation()
        results = simulation.run(verbose=False)

        self.assertEqual(
            results["arrived"],
            results["passed"] + results["remaining"]
        )

    def test_vehicle_departure_interval(self):

        simulation = self.make_simulation()

        initial_departures = simulation.total_departed

        simulation.move_vehicles(0, "NS_GREEN")

        # One second is not enough for a vehicle.
        self.assertEqual(
            simulation.total_departed,
            initial_departures
        )

        simulation.move_vehicles(1, "NS_GREEN")

        # Two seconds permit one vehicle
        # from each nonempty active approach.
        self.assertEqual(
            simulation.total_departed,
            initial_departures + 2
        )

    def test_red_signal_blocks_vehicles(self):

        simulation = self.make_simulation()

        simulation.move_vehicles(0, "ALL_RED")
        simulation.move_vehicles(1, "ALL_RED")

        self.assertEqual(simulation.total_departed, 0)

    def test_green_timer_resets_after_red(self):

        simulation = self.make_simulation()

        simulation.move_vehicles(0, "NS_GREEN")
        simulation.move_vehicles(1, "ALL_RED")
        simulation.move_vehicles(2, "NS_GREEN")

        # Only one uninterrupted second of green.
        self.assertEqual(simulation.total_departed, 0)

        simulation.move_vehicles(3, "NS_GREEN")

        self.assertEqual(simulation.total_departed, 2)

    def test_no_negative_waiting_times(self):

        simulation = self.make_simulation()
        simulation.run(verbose=False)

        for road in simulation.roads.values():

            for wait in road.completed_wait_times:
                self.assertGreaterEqual(wait, 0)


if __name__ == "__main__":
    unittest.main()
