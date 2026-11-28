
from core.engine import TrafficSimulation

from controllers.fixed_time import FixedTimeController
from controllers.adaptive import AdaptiveController


def compare_controllers():

    print("\nTRAFLO - CONTROLLER COMPARISON")

    # Experiment 1: Fixed-time controller
    fixed_controller = FixedTimeController()

    fixed_simulation = TrafficSimulation(
        fixed_controller
    )

    fixed_results = fixed_simulation.run(
        verbose=True
    )

    # Experiment 2: Adaptive controller
    adaptive_controller = AdaptiveController()

    adaptive_simulation = TrafficSimulation(
        adaptive_controller
    )

    adaptive_results = adaptive_simulation.run(
        verbose=True
    )

    # Both experiments must receive the same vehicles.
    assert (
        fixed_results["arrived"]
        == adaptive_results["arrived"]
    )

    print("\n" + "=" * 60)
    print("FINAL CONTROLLER COMPARISON")
    print("=" * 60)

    print(
        f"{'Metric':<25}"
        f"{'Fixed':>15}"
        f"{'Adaptive':>15}"
    )

    print("-" * 55)

    metrics = [
        ("Vehicles passed", "passed"),
        ("Remaining vehicles", "remaining"),
        ("Queue seconds", "queue_seconds"),
        ("Accrued wait/arrival", "average_wait_per_arrival")
    ]

    for label, key in metrics:

        fixed_value = fixed_results[key]
        adaptive_value = adaptive_results[key]

        print(
            f"{label:<25}"
            f"{fixed_value:>15.2f}"
            f"{adaptive_value:>15.2f}"
        )

    fixed_wait = fixed_results["average_wait_per_arrival"]
    adaptive_wait = adaptive_results["average_wait_per_arrival"]

    if fixed_wait > 0:

        improvement = (
            (fixed_wait - adaptive_wait)
            / fixed_wait
        ) * 100

        print(
            f"\nAdaptive wait improvement: "
            f"{improvement:.2f}%"
        )

    else:
        print(
            "\nNo fixed-controller waiting time "
            "to calculate percentage improvement."
        )


if __name__ == "__main__":
    compare_controllers()
