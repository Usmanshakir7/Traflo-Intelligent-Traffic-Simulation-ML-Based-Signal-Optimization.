"""Traflo machine-learning-assisted traffic signal controller."""
from pathlib import Path
import joblib
import pandas as pd

from config.settings import ARRIVAL_INTERVALS, CLEARANCE_TIME
from controllers.base import TrafficController

DEFAULT_MODEL_PATH = (
    Path(__file__).resolve().parents[1]
    / "ml" / "models" / "random_forest.joblib"
)


class MLController(TrafficController):
    def __init__(self, arrival_intervals=None, model_path=None):
        self.name = "ML-Assisted Controller"
        model_path = Path(model_path) if model_path else DEFAULT_MODEL_PATH
        if not model_path.is_file():
            raise FileNotFoundError(
                f"Trained model not found: {model_path}. Run 'python -m ml.train' first."
            )

        # Load only a model that we trained and saved ourselves.
        bundle = joblib.load(model_path)
        self.model = bundle["model"]
        self.features = bundle["features"]
        self.green_choices = sorted(int(v) for v in bundle["green_choices"])
        self.total_green_time = int(bundle["total_green_time"])
        self.cycle_duration = self.total_green_time + 2 * CLEARANCE_TIME

        self.arrival_intervals = dict(
            ARRIVAL_INTERVALS if arrival_intervals is None else arrival_intervals
        )
        self.ns_green = self.total_green_time // 2
        self.ew_green = self.total_green_time - self.ns_green
        self.decision_history = []

    def calculate_green_times(self, queues, current_time):
        candidate_rows = []
        for ns_green in self.green_choices:
            candidate_rows.append({
                "north_queue": queues["North"],
                "south_queue": queues["South"],
                "east_queue": queues["East"],
                "west_queue": queues["West"],
                "north_interval": self.arrival_intervals["North"],
                "south_interval": self.arrival_intervals["South"],
                "east_interval": self.arrival_intervals["East"],
                "west_interval": self.arrival_intervals["West"],
                "ns_green": ns_green,
                "ew_green": self.total_green_time - ns_green,
            })

        candidates = pd.DataFrame(candidate_rows)[self.features]
        predictions = self.model.predict(candidates)
        best_index = min(range(len(predictions)), key=lambda i: predictions[i])
        self.ns_green = self.green_choices[best_index]
        self.ew_green = self.total_green_time - self.ns_green

        self.decision_history.append({
            "time": current_time,
            "ns_green": self.ns_green,
            "ew_green": self.ew_green,
            "predicted_queue_seconds": float(predictions[best_index]),
        })

    def get_signal(self, current_time, queues=None):
        cycle_time = current_time % self.cycle_duration
        if cycle_time == 0:
            if queues is None:
                raise ValueError("ML controller needs current traffic queues.")
            self.calculate_green_times(queues, current_time)

        ns_end = self.ns_green
        clearance_end = ns_end + CLEARANCE_TIME
        ew_end = clearance_end + self.ew_green

        if cycle_time < ns_end:
            return "NS_GREEN"
        if cycle_time < clearance_end:
            return "ALL_RED"
        if cycle_time < ew_end:
            return "EW_GREEN"
        return "ALL_RED"
