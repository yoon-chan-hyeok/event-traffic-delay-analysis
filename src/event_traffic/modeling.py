"""Leakage-aware model comparison for grouped traffic observations."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def evaluate_regressors_by_group(
    frame: pd.DataFrame,
    *,
    x_column: str,
    y_column: str,
    group_column: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Evaluate a mean baseline, linear model and isotonic model by held-out group.

    Every observation from the held-out date stays out of model fitting. Signed
    delays remain in the data; the function does not silently remove them.
    """
    required = {x_column, y_column, group_column}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"Missing modeling columns: {', '.join(missing)}")

    data = frame[[x_column, y_column, group_column]].dropna().copy().reset_index(drop=True)
    if data[group_column].nunique() < 3:
        raise ValueError("At least three groups are required for grouped evaluation")
    predictions: list[dict[str, object]] = []

    for held_out in sorted(data[group_column].unique()):
        train = data[data[group_column] != held_out]
        test = data[data[group_column] == held_out]
        x_train = train[x_column].to_numpy(dtype=float)
        y_train = train[y_column].to_numpy(dtype=float)
        x_test = test[x_column].to_numpy(dtype=float)

        mean_prediction = np.repeat(y_train.mean(), len(test))
        linear = LinearRegression().fit(x_train.reshape(-1, 1), y_train)
        linear_prediction = linear.predict(x_test.reshape(-1, 1))
        order = np.argsort(x_train)
        isotonic = IsotonicRegression(increasing=True, out_of_bounds="clip").fit(
            x_train[order], y_train[order]
        )
        isotonic_prediction = isotonic.predict(x_test)

        for model_name, values in (
            ("MeanBaseline", mean_prediction),
            ("LinearRegression", linear_prediction),
            ("IsotonicRegression", isotonic_prediction),
        ):
            for row_index, prediction in zip(test.index, values, strict=True):
                predictions.append(
                    {
                        "row_index": int(row_index),
                        "held_out_group": str(held_out),
                        "model": model_name,
                        "actual": float(data.loc[row_index, y_column]),
                        "prediction": float(prediction),
                    }
                )

    prediction_frame = pd.DataFrame(predictions)
    summaries = []
    for model_name, rows in prediction_frame.groupby("model", sort=False):
        summaries.append(
            {
                "model": model_name,
                "observations": len(rows),
                "held_out_groups": rows["held_out_group"].nunique(),
                "mae": mean_absolute_error(rows["actual"], rows["prediction"]),
                "rmse": mean_squared_error(
                    rows["actual"], rows["prediction"]
                ) ** 0.5,
                "r2": r2_score(rows["actual"], rows["prediction"]),
            }
        )
    summary_frame = pd.DataFrame(summaries).sort_values("mae", ignore_index=True)
    return summary_frame, prediction_frame


def fit_isotonic_curve(
    frame: pd.DataFrame, *, x_column: str, y_column: str
) -> IsotonicRegression:
    """Fit the final monotonic curve after validation has been reported."""
    data = frame[[x_column, y_column]].dropna().sort_values(x_column)
    if len(data) < 2:
        raise ValueError("At least two observations are required")
    return IsotonicRegression(increasing=True, out_of_bounds="clip").fit(
        data[x_column].to_numpy(dtype=float),
        data[y_column].to_numpy(dtype=float),
    )
