
from controllers.base import TrafficController

from config.settings import (
    NORTH_SOUTH_GREEN,
    EAST_WEST_GREEN,
    CLEARANCE_TIME
)


class FixedTimeController(TrafficController):

    def __init__(self):
        self.name = "Fixed-Time Controller"

        self.cycle_duration = (
            NORTH_SOUTH_GREEN
            + EAST_WEST_GREEN
            + 2 * CLEARANCE_TIME
        )

    def get_signal(self, current_time, queues=None):

        cycle_time = current_time % self.cycle_duration

        ns_end = NORTH_SOUTH_GREEN
        clearance_end = ns_end + CLEARANCE_TIME
        ew_end = clearance_end + EAST_WEST_GREEN

        if cycle_time < ns_end:
            return "NS_GREEN"

        elif cycle_time < clearance_end:
            return "ALL_RED"

        elif cycle_time < ew_end:
            return "EW_GREEN"

        else:
            return "ALL_RED"
