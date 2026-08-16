import numpy as np
import pandas as pd

from event_traffic.preprocessing import (
    compare_event_to_baseline,
    daily_od_profile,
    prepare_od,
)


def _row(date: str, count: int, duration: int, modal: float = 0) -> dict:
    return {
        "origin_hdong_cd": "1111051500",
        "dest_hdong_cd": "1156054000",
        "date": date,
        "start_time": "18:00",
        "end_time": "19:00",
        "modal": modal,
        "od_dist_avg": 10_000,
        "od_duration_avg": duration,
        "od_cnts": count,
    }


def test_baseline_uses_observed_dates_instead_of_fixed_divisor():
    raw = pd.DataFrame(
        [
            _row("20231007", 300, 30),
            _row("20230909", 90, 20),
            _row("20230916", 150, 24),
        ]
    )
    profile = daily_od_profile(
        prepare_od(raw), hdong_code="1156054000", direction="arrival", mode="car"
    )
    compared = compare_event_to_baseline(profile, event_date="20231007")

    assert compared.loc[0, "baseline_days"] == 2
    assert compared.loc[0, "baseline_trip_count"] == 120
    assert compared.loc[0, "excess_trip_count"] == 180


def test_missing_mode_is_not_reclassified_as_car():
    raw = pd.DataFrame(
        [
            _row("20231007", 300, 30, modal=0),
            _row("20231007", 999, 30, modal=np.nan),
            _row("20230909", 100, 20, modal=0),
        ]
    )
    profile = daily_od_profile(
        prepare_od(raw), hdong_code="1156054000", direction="arrival", mode="car"
    )
    event_count = profile.loc[profile["date"] == "20231007", "trip_count"].iloc[0]
    assert event_count == 300


def test_duration_is_weighted_by_trip_count():
    raw = pd.DataFrame(
        [
            _row("20231007", 1, 10),
            _row("20231007", 9, 30),
            _row("20230909", 10, 20),
        ]
    )
    profile = daily_od_profile(
        prepare_od(raw), hdong_code="1156054000", direction="arrival"
    )
    value = profile.loc[profile["date"] == "20231007", "avg_duration_min"].iloc[0]
    assert value == 28
