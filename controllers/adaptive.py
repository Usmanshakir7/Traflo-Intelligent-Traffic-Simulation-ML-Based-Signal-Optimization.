
from controllers.base import TrafficController
from config.settings import CLEARANCE_TIME


class AdaptiveController(TrafficController):

    def __init__(self):

        self.name = "Rule-Based Adaptive Controller"

        self.total_green_time = 60
        self.min_green = 20
        self.max_green = 40

        self.cycle_duration = (
            self.total_green_time
            + 2 * CLEARANCE_TIME
        )

        self.ns_green = 30
        self.ew_green = 30

    def calculate_green_times(self, queues):

        ns_cars = (
            queues["North"]
            + queues["South"]
        )

        ew_cars = (
            queues["East"]
            + queues["West"]
        )

        total_cars = ns_cars + ew_cars

        if total_cars == 0:
            self.ns_green = 30

        else:
            proposed_time = round(
                self.total_green_time
                * ns_cars / total_cars
            )

            self.ns_green = max(
                self.min_green,
                min(self.max_green, proposed_time)
            )

        self.ew_green = (
            self.total_green_time
            - self.ns_green
        )

    def get_signal(self, current_time, queues=None):

        cycle_time = current_time % self.cycle_duration

        # Recalculate once at the beginning
        # of each full traffic signal cycle.
        if cycle_time == 0:

            if queues is None:
                raise ValueError(
                    "Adaptive controller needs traffic queues."
                )

            self.calculate_green_times(queues)

        ns_end = self.ns_green

        clearance_end = (
            ns_end + CLEARANCE_TIME
        )

        ew_end = (
            clearance_end + self.ew_green
        )

        if cycle_time < ns_end:
            return "NS_GREEN"

        elif cycle_time < clearance_end:
            return "ALL_RED"

        elif cycle_time < ew_end:
            return "EW_GREEN"

        else:
            return "ALL_RED"
