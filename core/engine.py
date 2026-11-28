
from config.settings import (
    SIMULATION_DURATION,
    SECONDS_PER_VEHICLE,
    INITIAL_VEHICLES,
    ARRIVAL_INTERVALS
)

from core.vehicles import VehicleQueue


class TrafficSimulation:

    def __init__(self, controller):

        self.controller = controller

        self.roads = {
            road: VehicleQueue(road)
            for road in INITIAL_VEHICLES
        }

        self.total_arrived = 0
        self.total_departed = 0
        self.total_queue_seconds = 0

        self.history = []

        # Add starting vehicles.
        for road, count in INITIAL_VEHICLES.items():

            for _ in range(count):
                self.roads[road].add_vehicle(0)

            self.total_arrived += count

    def get_queue_counts(self):

        return {
            name: road.get_queue_length()
            for name, road in self.roads.items()
        }

    def add_new_vehicles(self, current_time):

        for road, interval in ARRIVAL_INTERVALS.items():

            if (
                current_time > 0
                and current_time % interval == 0
            ):

                self.roads[road].add_vehicle(current_time)
                self.total_arrived += 1

    def move_vehicles(self, current_time, signal):

        if current_time % SECONDS_PER_VEHICLE != 0:
            return

        if signal == "NS_GREEN":
            active_roads = ["North", "South"]

        elif signal == "EW_GREEN":
            active_roads = ["East", "West"]

        else:
            active_roads = []

        for road in active_roads:

            moved = self.roads[road].release_vehicle(
                current_time
            )

            if moved:
                self.total_departed += 1

    def get_total_waiting(self):

        return sum(
            road.get_queue_length()
            for road in self.roads.values()
        )

    def run(self, verbose=True):

        if verbose:
            print("\n" + "=" * 60)
            print(self.controller.name.upper())
            print("=" * 60)

        previous_signal = None

        for current_time in range(SIMULATION_DURATION):

            # 1. Generate vehicle arrivals.
            self.add_new_vehicles(current_time)

            # 2. Read the current traffic.
            queues = self.get_queue_counts()

            # 3. Controller chooses the signal.
            signal = self.controller.get_signal(
                current_time,
                queues
            )

            # 4. Move vehicles on green approaches.
            self.move_vehicles(current_time, signal)

            # 5. Record time spent by vehicles still waiting.
            self.total_queue_seconds += self.get_total_waiting()

            # 6. Save simulation state for future charts.
            self.history.append({
                "time": current_time,
                "signal": signal,
                "queues": self.get_queue_counts(),
                "total_waiting": self.get_total_waiting(),
                "total_departed": self.total_departed
            })

            if verbose:

                if signal != previous_signal:

                    print(
                        f"\nTime {current_time}s: "
                        f"{signal}"
                    )

                    previous_signal = signal

                if current_time % 10 == 0:

                    print(
                        f"Time: {current_time:3}s | "
                        f"Waiting: {self.get_total_waiting():3} | "
                        f"Passed: {self.total_departed:3}"
                    )

        results = self.get_results()

        if verbose:
            self.show_results(results)

        return results

    def get_results(self):

        completed_waits = []

        for road in self.roads.values():
            completed_waits.extend(
                road.completed_wait_times
            )

        average_completed_wait = (
            sum(completed_waits) / len(completed_waits)
            if completed_waits else 0
        )

        # Includes waiting accumulated by unfinished vehicles.
        average_wait_per_arrival = (
            self.total_queue_seconds / self.total_arrived
            if self.total_arrived else 0
        )

        remaining = self.get_total_waiting()

        assert (
            self.total_arrived
            == self.total_departed + remaining
        ), "Vehicle accounting error!"

        return {
            "controller": self.controller.name,
            "arrived": self.total_arrived,
            "passed": self.total_departed,
            "remaining": remaining,
            "average_completed_wait": average_completed_wait,
            "average_wait_per_arrival": average_wait_per_arrival,
            "queue_seconds": self.total_queue_seconds
        }

    def show_results(self, results):

        print("\nFINAL RESULTS")
        print("-" * 60)

        print(f"Arrived:   {results['arrived']}")
        print(f"Passed:    {results['passed']}")
        print(f"Remaining: {results['remaining']}")

        print(
            "Average completed wait: "
            f"{results['average_completed_wait']:.2f} sec"
        )

        print(
            "Accrued wait per arrival: "
            f"{results['average_wait_per_arrival']:.2f} sec"
        )

        print("\nRemaining queues:")

        for road, count in self.get_queue_counts().items():
            print(f"{road}: {count}")

        print("\nVehicle accounting verified.")
