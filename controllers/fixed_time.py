from controllers.base import TrafficController
from config.settings import NORTH_SOUTH_GREEN, EAST_WEST_GREEN, CLEARANCE_TIME


class FixedTimeController(TrafficController):
    def __init__(self, ns_green=None, ew_green=None):
        self.name = "Fixed-Time Controller"
        self.ns_green = NORTH_SOUTH_GREEN if ns_green is None else ns_green
        self.ew_green = EAST_WEST_GREEN if ew_green is None else ew_green

        if self.ns_green <= 0 or self.ew_green <= 0 or CLEARANCE_TIME < 0:
            raise ValueError("Signal timings must be valid.")

        self.cycle_duration = (
            self.ns_green + self.ew_green + 2 * CLEARANCE_TIME
        )

    def get_signal(self, current_time, queues=None):
        cycle_time = current_time % self.cycle_duration
        ns_end = self.ns_green
        clearance_end = ns_end + CLEARANCE_TIME
        ew_end = clearance_end + self.ew_green

        if cycle_time < ns_end:
            return "NS_GREEN"
        elif cycle_time < clearance_end:
            return "ALL_RED"
        elif cycle_time < ew_end:
            return "EW_GREEN"
        else:
            return "ALL_RED"
