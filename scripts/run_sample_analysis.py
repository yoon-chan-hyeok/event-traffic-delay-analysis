"""Run the public synthetic sample from preprocessing through scenario output."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from event_traffic.modeling import evaluate_regressors_by_group, fit_isotonic_curve
from event_traffic.preprocessing import compare_event_to_baseline, daily_od_profile, prepare_od
from event_traffic.scenario import shuttle_capacity


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DIR = ROOT / "data" / "sample"
OUTPUT_DIR = ROOT / "results" / "sample"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    od = prepare_od(pd.read_csv(SAMPLE_DIR / "od_sample.csv", dtype={"date": str}))
    profile = daily_od_profile(
        od,
        hdong_code="1156054000",
        direction="arrival",
        mode="car",
    )
    compared = compare_event_to_baseline(profile, event_date="20231007")
    compared.to_csv(OUTPUT_DIR / "event_vs_baseline.csv", index=False)

    observations = pd.read_csv(SAMPLE_DIR / "delay_observations.csv")
    validation, predictions = evaluate_regressors_by_group(
        observations,
        x_column="excess_trip_index",
        y_column="delay_min",
        group_column="observation_date",
    )
    validation.to_csv(OUTPUT_DIR / "model_validation.csv", index=False)
    predictions.to_csv(OUTPUT_DIR / "out_of_fold_predictions.csv", index=False)

    scenario = shuttle_capacity(
        seats_per_bus=45,
        buses=100,
        rotations=3,
        demand=13_000,
        cost_per_bus=500_000,
    )
    (OUTPUT_DIR / "scenario_summary.json").write_text(
        json.dumps(scenario, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    _plot_event_comparison(compared)
    _plot_delay_curve(observations)
    print(validation.to_string(index=False))
    print(f"Sample outputs written to {OUTPUT_DIR}")


def _plot_event_comparison(compared: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.plot(compared["time"], compared["event_trip_count"], marker="o", label="Event date")
    ax.plot(
        compared["time"],
        compared["baseline_trip_count"],
        marker="o",
        label="Reference-date mean",
    )
    ax.set(title="Synthetic event and reference profiles", xlabel="Arrival time", ylabel="Trip count")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "event_vs_baseline.png", dpi=150)
    plt.close(fig)


def _plot_delay_curve(observations: pd.DataFrame) -> None:
    model = fit_isotonic_curve(
        observations, x_column="excess_trip_index", y_column="delay_min"
    )
    grid = np.linspace(observations["excess_trip_index"].min(), observations["excess_trip_index"].max(), 200)
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.scatter(
        observations["excess_trip_index"], observations["delay_min"], alpha=0.65, label="Synthetic observations"
    )
    ax.plot(grid, model.predict(grid), color="#d97706", linewidth=2.5, label="Isotonic fit")
    ax.axhline(0, color="#64748b", linewidth=1)
    ax.set(title="Synthetic monotonic delay example", xlabel="Excess-trip index", ylabel="Travel-time difference (min)")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "demand_delay_curve.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
