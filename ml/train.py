"""Train and evaluate Traflo's Random Forest congestion predictor."""
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupShuffleSplit

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "traffic_training.csv"
MODEL_FOLDER = PROJECT_ROOT / "ml" / "models"
MODEL_PATH = MODEL_FOLDER / "random_forest.joblib"
REPORT_PATH = MODEL_FOLDER / "training_report.json"
RANDOM_SEED = 42

FEATURES = [
    "north_queue", "south_queue", "east_queue", "west_queue",
    "north_interval", "south_interval", "east_interval", "west_interval",
    "ns_green", "ew_green",
]
TARGET = "queue_seconds"


def load_dataset():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}. Run python -m ml.generate_data"
        )
    data = pd.read_csv(DATA_PATH)
    required = FEATURES + [TARGET, "scenario_id"]
    missing = [column for column in required if column not in data.columns]
    if missing:
        raise ValueError(f"Dataset is missing columns: {missing}")
    if data[required].isnull().any().any():
        raise ValueError("Dataset contains missing values.")
    if data["scenario_id"].nunique() < 10:
        raise ValueError("At least 10 traffic scenarios are required.")
    if 30 not in data["ns_green"].values:
        raise ValueError("A 30/30 fixed-time baseline is required.")
    return data


def split_dataset(data):
    splitter = GroupShuffleSplit(
        n_splits=1, test_size=0.20, random_state=RANDOM_SEED
    )
    train_indices, test_indices = next(
        splitter.split(data[FEATURES], data[TARGET], groups=data["scenario_id"])
    )
    train_data = data.iloc[train_indices].copy()
    test_data = data.iloc[test_indices].copy()
    assert set(train_data["scenario_id"]).isdisjoint(set(test_data["scenario_id"]))
    return train_data, test_data


def train_model(train_data):
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=14,
        min_samples_leaf=2,
        random_state=RANDOM_SEED,
        n_jobs=-1,
    )
    model.fit(train_data[FEATURES], train_data[TARGET])
    return model


def evaluate_predictions(model, test_data):
    predictions = model.predict(test_data[FEATURES])
    actual = test_data[TARGET]
    return {
        "mae": float(mean_absolute_error(actual, predictions)),
        "rmse": float(np.sqrt(mean_squared_error(actual, predictions))),
        "r2": float(r2_score(actual, predictions)),
    }


def evaluate_timing_choices(model, test_data):
    evaluation = test_data.copy()
    evaluation["predicted_queue_seconds"] = model.predict(evaluation[FEATURES])

    ml_indices = evaluation.groupby("scenario_id")[
        "predicted_queue_seconds"
    ].idxmin()
    ml_choices = evaluation.loc[ml_indices].set_index("scenario_id").sort_index()

    optimal_indices = evaluation.groupby("scenario_id")[TARGET].idxmin()
    best_choices = evaluation.loc[optimal_indices].set_index("scenario_id").sort_index()

    fixed_choices = (
        evaluation[evaluation["ns_green"] == 30]
        .set_index("scenario_id").sort_index()
    )
    if not ml_choices.index.equals(fixed_choices.index):
        raise ValueError("Every test scenario needs a 30/30 baseline.")

    fixed_wait = float(fixed_choices[TARGET].mean())
    ml_wait = float(ml_choices[TARGET].mean())
    best_wait = float(best_choices[TARGET].mean())
    improvement = (
        100 * (fixed_wait - ml_wait) / fixed_wait if fixed_wait > 0 else 0.0
    )
    regret = float((ml_choices[TARGET] - best_choices[TARGET]).mean())
    optimal_rate = float(
        100 * np.isclose(
            ml_choices[TARGET].to_numpy(),
            best_choices[TARGET].to_numpy()
        ).mean()
    )
    return {
        "fixed_mean_queue_seconds": fixed_wait,
        "ml_mean_queue_seconds": ml_wait,
        "best_mean_queue_seconds": best_wait,
        "improvement_percent": improvement,
        "mean_regret": regret,
        "optimal_choice_rate": optimal_rate,
    }


def save_artifacts(model, data, report):
    MODEL_FOLDER.mkdir(parents=True, exist_ok=True)
    model_bundle = {
        "model": model,
        "features": FEATURES,
        "target": TARGET,
        "green_choices": sorted(
            int(value) for value in data["ns_green"].unique()
        ),
        "total_green_time": int(
            (data["ns_green"] + data["ew_green"]).iloc[0]
        ),
    }
    joblib.dump(model_bundle, MODEL_PATH)
    with open(REPORT_PATH, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)


def main():
    print("\nTRAFLO - MACHINE LEARNING TRAINING")
    print("=" * 55)

    data = load_dataset()
    train_data, test_data = split_dataset(data)

    print(f"Dataset rows: {len(data)}")
    print(f"Traffic scenarios: {data['scenario_id'].nunique()}")
    print(f"\nTraining rows: {len(train_data)}")
    print(f"Testing rows:  {len(test_data)}")
    print(f"Training scenarios: {train_data['scenario_id'].nunique()}")
    print(f"Testing scenarios: {test_data['scenario_id'].nunique()}")

    print("\nTraining Random Forest...")
    model = train_model(train_data)
    prediction_metrics = evaluate_predictions(model, test_data)
    timing_metrics = evaluate_timing_choices(model, test_data)

    print("\nMODEL PREDICTION RESULTS")
    print("-" * 55)
    print(f"MAE:  {prediction_metrics['mae']:.2f}")
    print(f"RMSE: {prediction_metrics['rmse']:.2f}")
    print(f"R2:   {prediction_metrics['r2']:.4f}")

    print("\nML TIMING DECISION COMPARISON")
    print("-" * 55)
    print(f"Fixed-time mean queue-seconds: {timing_metrics['fixed_mean_queue_seconds']:.2f}")
    print(f"ML-selected mean queue-seconds: {timing_metrics['ml_mean_queue_seconds']:.2f}")
    print(f"Best possible tested mean: {timing_metrics['best_mean_queue_seconds']:.2f}")
    print(f"ML improvement over fixed: {timing_metrics['improvement_percent']:+.2f}%")
    print(f"Mean regret vs best timing: {timing_metrics['mean_regret']:.2f}")
    print(f"Optimal timing selection rate: {timing_metrics['optimal_choice_rate']:.2f}%")

    report = {
        "dataset_rows": len(data),
        "training_rows": len(train_data),
        "testing_rows": len(test_data),
        "training_scenarios": int(train_data["scenario_id"].nunique()),
        "testing_scenarios": int(test_data["scenario_id"].nunique()),
        "prediction_metrics": prediction_metrics,
        "timing_metrics": timing_metrics,
        "feature_importance": {
            feature: float(importance)
            for feature, importance in zip(FEATURES, model.feature_importances_)
        },
    }
    save_artifacts(model, data, report)

    print("\nTRAINING COMPLETE")
    print("=" * 55)
    print(f"Model saved: {MODEL_PATH}")
    print(f"Report saved: {REPORT_PATH}")


if __name__ == "__main__":
    main()
