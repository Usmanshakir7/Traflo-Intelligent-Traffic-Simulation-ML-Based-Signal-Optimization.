
"""One-intersection discrete-time traffic simulator."""

from config.settings import (
    SIMULATION_DURATION,
    SECONDS_PER_VEHICLE,
    INITIAL_VEHICLES,
    ARRIVAL_INTERVALS,
)
from core.vehicles import VehicleQueue


class TrafficSimulation:
    """Run either controller on a configurable, reproducible traffic scenario."""

    def __init__(
        self,
        controller,
        initial_vehicles=None,
        arrival_intervals=None,
        duration=None,
    ):
        self.controller = controller
        self.initial_vehicles = dict(
            INITIAL_VEHICLES if initial_vehicles is None else initial_vehicles
        )
        self.arrival_intervals = dict(
            ARRIVAL_INTERVALS if arrival_intervals is None else arrival_intervals
        )
        self.duration = SIMULATION_DURATION if duration is None else duration

        roads = {"North", "South", "East", "West"}
        if set(self.initial_vehicles) != roads or set(self.arrival_intervals) != roads:
            raise ValueError("Specify all four roads: North, South, East, West.")
        if not isinstance(self.duration, int) or self.duration <= 0:
            raise ValueError("Simulation duration must be a positive integer.")
        if SECONDS_PER_VEHICLE <= 0:
            raise ValueError("SECONDS_PER_VEHICLE must be positive.")
        if any(count < 0 for count in self.initial_vehicles.values()):
            raise ValueError("Initial vehicle counts cannot be negative.")
        if any(interval <= 0 for interval in self.arrival_intervals.values()):
            raise ValueError("Arrival intervals must be positive.")

        self.roads = {name: VehicleQueue(name) for name in self.initial_vehicles}
        self.total_arrived = 0
        self.total_departed = 0
        self.total_queue_seconds = 0
        self.history = []
        self.active_signal = None
        self.green_elapsed = 0

        for road, count in self.initial_vehicles.items():
            for _ in range(count):
                self.roads[road].add_vehicle(0)
            self.total_arrived += count

    def get_queue_counts(self):
        return {name: road.get_queue_length() for name, road in self.roads.items()}

    def add_new_vehicles(self, current_time):
        for road, interval in self.arrival_intervals.items():
            if current_time > 0 and current_time % interval == 0:
                self.roads[road].add_vehicle(current_time)
                self.total_arrived += 1

    def move_vehicles(self, current_time, signal):
        if signal not in {"NS_GREEN", "EW_GREEN", "ALL_RED"}:
            raise ValueError(f"Unknown traffic signal: {signal}")

        if signal != self.active_signal:
            self.active_signal = signal
            self.green_elapsed = 0

        if signal == "ALL_RED":
            return

        self.green_elapsed += 1
        if self.green_elapsed % SECONDS_PER_VEHICLE != 0:
            return

        active_roads = ["North", "South"] if signal == "NS_GREEN" else ["East", "West"]
        departure_time = current_time + 1
        for road in active_roads:
            if self.roads[road].release_vehicle(departure_time):
                self.total_departed += 1

    def get_total_waiting(self):
        return sum(road.get_queue_length() for road in self.roads.values())

    def run(self, verbose=True):
        if verbose:
            print(f"\n{'=' * 60}\n{self.controller.name.upper()}\n{'=' * 60}")

        previous_signal = None
        for current_time in range(self.duration):
            self.add_new_vehicles(current_time)
            signal = self.controller.get_signal(current_time, self.get_queue_counts())
            self.move_vehicles(current_time, signal)
            remaining = self.get_total_waiting()
            self.total_queue_seconds += remaining
            self.history.append({
                "time": current_time + 1,
                "signal": signal,
                "queues": self.get_queue_counts(),
                "total_waiting": remaining,
                "total_departed": self.total_departed,
                "green_elapsed": self.green_elapsed,
            })
            if verbose:
                if signal != previous_signal:
                    print(f"Time {current_time}s: {signal}")
                    previous_signal = signal
                if current_time % 10 == 0:
                    print(f"Time: {current_time:3}s | Waiting: {remaining:3} | Passed: {self.total_departed:3}")

        results = self.get_results()
        if verbose:
            self.show_results(results)
        return results

    def get_results(self):
        waits = [w for road in self.roads.values() for w in road.completed_wait_times]
        remaining = self.get_total_waiting()
        if self.total_arrived != self.total_departed + remaining:
            raise AssertionError("Vehicle accounting error!")
        return {
            "controller": self.controller.name,
            "arrived": self.total_arrived,
            "passed": self.total_departed,
            "remaining": remaining,
            "average_completed_wait": sum(waits) / len(waits) if waits else 0.0,
            "average_wait_per_arrival": (
                self.total_queue_seconds / self.total_arrived if self.total_arrived else 0.0
            ),
            "queue_seconds": self.total_queue_seconds,
            "history": self.history,
        }

    def show_results(self, results):
        print("\nFINAL RESULTS\n" + "-" * 60)
        print(f"Arrived: {results['arrived']}")
        print(f"Passed: {results['passed']}")
        print(f"Remaining: {results['remaining']}")
        print(f"Average completed wait: {results['average_completed_wait']:.2f} sec")
        print(f"Accrued wait per arrival: {results['average_wait_per_arrival']:.2f} sec")
        print("\nRemaining queues:")
        for road, count in self.get_queue_counts().items():
            print(f"{road}: {count}")
        print("\nVehicle accounting verified.")
