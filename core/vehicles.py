
from collections import deque


class VehicleQueue:

    def __init__(self, road_name):
        self.road_name = road_name
        self.vehicles = deque()
        self.completed_wait_times = []

    def add_vehicle(self, arrival_time):
        self.vehicles.append(arrival_time)

    def release_vehicle(self, current_time):
        if not self.vehicles:
            return False

        arrival_time = self.vehicles.popleft()

        waiting_time = current_time - arrival_time

        self.completed_wait_times.append(waiting_time)

        return True

    def get_queue_length(self):
        return len(self.vehicles)

    def get_total_completed(self):
        return len(self.completed_wait_times)
