"""Generate reproducible synthetic traffic scenarios for Traflo."""
import csv
import random
from pathlib import Path

from config.settings import NORTH_SOUTH_GREEN, EAST_WEST_GREEN, CLEARANCE_TIME
from core.engine import TrafficSimulation
from controllers.fixed_time import FixedTimeController

RANDOM_SEED = 42
NUMBER_OF_SCENARIOS = 300
GREEN_CHOICES = [20, 25, 30, 35, 40]
TOTAL_GREEN = NORTH_SOUTH_GREEN + EAST_WEST_GREEN
CYCLE_DURATION = TOTAL_GREEN + 2 * CLEARANCE_TIME
ROADS = ["North", "South", "East", "West"]


def generate_traffic_scenario(rng, scenario_id):
    scenario_type = scenario_id % 4

    if scenario_type == 0:
        initial = {road: rng.randint(10, 40) for road in ROADS}
        intervals = {road: rng.randint(3, 8) for road in ROADS}
    elif scenario_type == 1:
        initial = {
            "North": rng.randint(35, 75), "South": rng.randint(35, 75),
            "East": rng.randint(5, 25), "West": rng.randint(5, 25)
        }
        intervals = {
            "North": rng.randint(2, 4), "South": rng.randint(2, 4),
            "East": rng.randint(6, 12), "West": rng.randint(6, 12)
        }
    elif scenario_type == 2:
        initial = {
            "North": rng.randint(5, 25), "South": rng.randint(5, 25),
            "East": rng.randint(35, 75), "West": rng.randint(35, 75)
        }
        intervals = {
            "North": rng.randint(6, 12), "South": rng.randint(6, 12),
            "East": rng.randint(2, 4), "West": rng.randint(2, 4)
        }
    else:
        initial = {road: rng.randint(0, 15) for road in ROADS}
        intervals = {road: rng.randint(7, 15) for road in ROADS}
    return initial, intervals


def run_candidate(initial, intervals, ns_green):
    controller = FixedTimeController(
        ns_green=ns_green, ew_green=TOTAL_GREEN - ns_green
    )
    simulation = TrafficSimulation(
        controller=controller,
        initial_vehicles=initial,
        arrival_intervals=intervals,
        duration=CYCLE_DURATION
    )
    return simulation.run(verbose=False)


def generate_dataset():
    rng = random.Random(RANDOM_SEED)
    data_folder = Path(__file__).resolve().parents[1] / "data"
    data_folder.mkdir(parents=True, exist_ok=True)
    output_path = data_folder / "traffic_training.csv"

    fieldnames = [
        "scenario_id", "north_queue", "south_queue",
        "east_queue", "west_queue",
        "north_interval", "south_interval", "east_interval", "west_interval",
        "ns_green", "ew_green", "queue_seconds",
        "vehicles_passed", "vehicles_remaining"
    ]
    row_count = 0
    with open(output_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for scenario_id in range(NUMBER_OF_SCENARIOS):
            initial, intervals = generate_traffic_scenario(rng, scenario_id)
            for ns_green in GREEN_CHOICES:
                results = run_candidate(initial, intervals, ns_green)
                writer.writerow({
                    "scenario_id": scenario_id,
                    "north_queue": initial["North"],
                    "south_queue": initial["South"],
                    "east_queue": initial["East"],
                    "west_queue": initial["West"],
                    "north_interval": intervals["North"],
                    "south_interval": intervals["South"],
                    "east_interval": intervals["East"],
                    "west_interval": intervals["West"],
                    "ns_green": ns_green,
                    "ew_green": TOTAL_GREEN - ns_green,
                    "queue_seconds": results["queue_seconds"],
                    "vehicles_passed": results["passed"],
                    "vehicles_remaining": results["remaining"],
                })
                row_count += 1

    print("\nTRAFLO - DATASET GENERATION COMPLETE")
    print("=" * 50)
    print(f"Traffic scenarios: {NUMBER_OF_SCENARIOS}")
    print(f"Timing options: {len(GREEN_CHOICES)}")
    print(f"Dataset rows: {row_count}")
    print(f"\nDataset saved to:\n{output_path}")


if __name__ == "__main__":
    generate_dataset()
