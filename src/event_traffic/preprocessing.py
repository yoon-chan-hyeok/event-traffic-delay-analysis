"""Preprocessing and event-versus-baseline aggregation."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd


OD_COLUMNS = {
    "origin_hdong_cd",
    "dest_hdong_cd",
    "date",
    "start_time",
    "end_time",
    "modal",
    "od_dist_avg",
    "od_duration_avg",
    "od_cnts",
}

MODE_CODES = {
    "car": {0},
    "public": {1, 2, 5},
}


def prepare_od(frame: pd.DataFrame, *, seoul_only: bool = True) -> pd.DataFrame:
    """Validate the raw OD schema and normalize types without hiding missing modes."""
    missing = sorted(OD_COLUMNS.difference(frame.columns))
    if missing:
        raise ValueError(f"Missing OD columns: {', '.join(missing)}")

    data = frame.loc[:, sorted(OD_COLUMNS)].copy()
    for column in ("origin_hdong_cd", "dest_hdong_cd", "date", "start_time", "end_time"):
        data[column] = data[column].astype("string").str.strip()

    data["modal"] = pd.to_numeric(data["modal"], errors="coerce").astype("Int64")
    for column in ("od_dist_avg", "od_duration_avg", "od_cnts"):
        data[column] = pd.to_numeric(data[column], errors="raise")

    if (data["od_dist_avg"] < 0).any():
        raise ValueError("od_dist_avg must be non-negative")
    if (data["od_duration_avg"] <= 0).any():
        raise ValueError("od_duration_avg must be positive")
    if (data["od_cnts"] < 0).any():
        raise ValueError("od_cnts must be non-negative")

    if seoul_only:
        data = data[
            data["origin_hdong_cd"].str.startswith("11", na=False)
            & data["dest_hdong_cd"].str.startswith("11", na=False)
        ]
    return data.reset_index(drop=True)


def daily_od_profile(
    frame: pd.DataFrame,
    *,
    hdong_code: str,
    direction: str,
    mode: str = "all",
    excluded_hours: Iterable[str] = (),
) -> pd.DataFrame:
    """Aggregate OD rows to one record per date and hour.

    Travel duration and speed are weighted by trip count. The mode filter is
    applied to event and baseline rows before either side is aggregated.
    """
    if direction not in {"arrival", "departure"}:
        raise ValueError("direction must be 'arrival' or 'departure'")
    if mode not in {"all", *MODE_CODES}:
        raise ValueError("mode must be 'all', 'car', or 'public'")

    location_column = "dest_hdong_cd" if direction == "arrival" else "origin_hdong_cd"
    time_column = "end_time" if direction == "arrival" else "start_time"
    data = frame[frame[location_column] == str(hdong_code)].copy()
    if mode != "all":
        data = data[data["modal"].isin(MODE_CODES[mode])]
    excluded = set(excluded_hours)
    if excluded:
        data = data[~data[time_column].isin(excluded)]
    if data.empty:
        raise ValueError("No OD rows remain after applying the requested filters")

    data["weighted_duration"] = data["od_duration_avg"] * data["od_cnts"]
    data["weighted_distance"] = data["od_dist_avg"] * data["od_cnts"]
    grouped = (
        data.groupby(["date", time_column], as_index=False, dropna=False)
        .agg(
            trip_count=("od_cnts", "sum"),
            weighted_duration=("weighted_duration", "sum"),
            weighted_distance=("weighted_distance", "sum"),
        )
        .rename(columns={time_column: "time"})
    )
    grouped["avg_duration_min"] = np.divide(
        grouped["weighted_duration"],
        grouped["trip_count"],
        out=np.full(len(grouped), np.nan, dtype=float),
        where=grouped["trip_count"].to_numpy() > 0,
    )
    grouped["avg_speed_kmh"] = np.divide(
        grouped["weighted_distance"] * 60.0 / 1000.0,
        grouped["weighted_duration"],
        out=np.full(len(grouped), np.nan, dtype=float),
        where=grouped["weighted_duration"].to_numpy() > 0,
    )
    return grouped[
        ["date", "time", "trip_count", "avg_duration_min", "avg_speed_kmh"]
    ].sort_values(["date", "time"], ignore_index=True)


def compare_event_to_baseline(profile: pd.DataFrame, *, event_date: str) -> pd.DataFrame:
    """Compare one event date with the mean of the observed baseline dates."""
    required = {"date", "time", "trip_count", "avg_duration_min", "avg_speed_kmh"}
    missing = sorted(required.difference(profile.columns))
    if missing:
        raise ValueError(f"Missing profile columns: {', '.join(missing)}")

    event_date = str(event_date)
    event = profile[profile["date"].astype(str) == event_date].copy()
    baseline = profile[profile["date"].astype(str) != event_date].copy()
    if event.empty:
        raise ValueError(f"Event date not found: {event_date}")
    if baseline["date"].nunique() < 1:
        raise ValueError("At least one baseline date is required")

    event = event.rename(
        columns={
            "trip_count": "event_trip_count",
            "avg_duration_min": "event_avg_duration_min",
            "avg_speed_kmh": "event_avg_speed_kmh",
        }
    )
    baseline_summary = baseline.groupby("time", as_index=False).agg(
        baseline_days=("date", "nunique"),
        baseline_trip_count=("trip_count", "mean"),
        baseline_avg_duration_min=("avg_duration_min", "mean"),
        baseline_avg_speed_kmh=("avg_speed_kmh", "mean"),
    )
    compared = event[
        ["time", "event_trip_count", "event_avg_duration_min", "event_avg_speed_kmh"]
    ].merge(baseline_summary, on="time", how="inner", validate="one_to_one")
    compared["excess_trip_count"] = (
        compared["event_trip_count"] - compared["baseline_trip_count"]
    )
    compared["relative_excess_trip_count"] = np.divide(
        compared["excess_trip_count"],
        compared["baseline_trip_count"],
        out=np.full(len(compared), np.nan, dtype=float),
        where=compared["baseline_trip_count"].to_numpy() > 0,
    )
    compared["delay_min"] = (
        compared["event_avg_duration_min"] - compared["baseline_avg_duration_min"]
    )
    return compared.sort_values("time", ignore_index=True)
