import numpy as np
import pandas as pd

from event_traffic.modeling import evaluate_regressors_by_group, fit_isotonic_curve


def _sample() -> pd.DataFrame:
    rows = []
    for group_index, date in enumerate(("d1", "d2", "d3", "d4")):
        for x in (0.0, 1.0, 2.0, 3.0):
            rows.append(
                {
                    "date": date,
                    "excess": x,
                    "delay": max(0.0, x * x / 3 + group_index * 0.05),
                }
            )
    return pd.DataFrame(rows)


def test_grouped_evaluation_produces_one_out_of_fold_prediction_per_model():
    data = _sample()
    summary, predictions = evaluate_regressors_by_group(
        data, x_column="excess", y_column="delay", group_column="date"
    )

    assert set(summary["model"]) == {
        "MeanBaseline",
        "LinearRegression",
        "IsotonicRegression",
    }
    assert len(predictions) == len(data) * 3
    assert summary["held_out_groups"].eq(4).all()


def test_final_isotonic_curve_is_non_decreasing():
    model = fit_isotonic_curve(_sample(), x_column="excess", y_column="delay")
    prediction = model.predict(np.linspace(0, 3, 20))
    assert np.all(np.diff(prediction) >= 0)
