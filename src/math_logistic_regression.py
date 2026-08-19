from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
)


CSV_FILE = "uk_school_student_data_50_students_attendance_linked.csv"

LOOKBACK = 3
FAIL_THRESHOLD = 40

OUTPUT_CSV = "math_failure_probability_predictions.csv"


# --------------------------------------------------
# 1. LOAD DATA
# --------------------------------------------------

data = pd.read_csv(CSV_FILE)

required_columns = {
    "student_id",
    "week",
    "subject",
    "score_percent",
    "attendance",
    "homework_completed",
}

missing = required_columns.difference(data.columns)

if missing:
    raise ValueError(
        "Missing columns: "
        + ", ".join(sorted(missing))
    )


# --------------------------------------------------
# 2. CLEAN DATA
# --------------------------------------------------

for column in [
    "week",
    "score_percent",
    "attendance",
    "homework_completed",
]:
    data[column] = pd.to_numeric(
        data[column],
        errors="coerce",
    )


# Mathematics only
math_data = data[
    data["subject"]
    .astype(str)
    .str.strip()
    .str.casefold()
    == "mathematics"
].copy()


math_data = math_data.dropna(
    subset=[
        "student_id",
        "week",
        "score_percent",
        "attendance",
        "homework_completed",
    ]
)


math_data = math_data.sort_values(
    [
        "student_id",
        "week",
    ]
)


# --------------------------------------------------
# 3. FEATURE ENGINEERING
# --------------------------------------------------

records = []


for student_id, student_data in math_data.groupby(
    "student_id"
):

    student_data = student_data.sort_values(
        "week"
    ).reset_index(drop=True)


    # Need LOOKBACK weeks plus a next week target
    for i in range(
        LOOKBACK,
        len(student_data)
    ):

        history = student_data.iloc[
            i - LOOKBACK:i
        ]

        target_row = student_data.iloc[i]


        # ------------------------------------------
        # RECENT SCORE FEATURES
        # ------------------------------------------

        recent_mean_score = (
            history["score_percent"].mean()
        )

        last_score = (
            history["score_percent"].iloc[-1]
        )


        # ------------------------------------------
        # SCORE TREND
        # ------------------------------------------

        weeks = history[
            "week"
        ].to_numpy(dtype=float)

        scores = history[
            "score_percent"
        ].to_numpy(dtype=float)


        slope, intercept = np.polyfit(
            weeks,
            scores,
            1,
        )


        # ------------------------------------------
        # ATTENDANCE
        # ------------------------------------------

        attendance_rate = (
            history["attendance"].mean()
        )


        # ------------------------------------------
        # HOMEWORK
        # ------------------------------------------

        homework_rate = (
            history[
                "homework_completed"
            ].mean()
        )


        # ------------------------------------------
        # SCORE VOLATILITY
        # ------------------------------------------

        score_volatility = (
            history[
                "score_percent"
            ].std(ddof=0)
        )


        # ------------------------------------------
        # TARGET
        # ------------------------------------------

        next_week_score = float(
            target_row[
                "score_percent"
            ]
        )


        failed_next_week = int(
            next_week_score
            < FAIL_THRESHOLD
        )


        records.append(
            {
                "student_id":
                    student_id,

                "prediction_week":
                    int(
                        target_row["week"]
                    ),

                "recent_mean_score":
                    recent_mean_score,

                "last_score":
                    last_score,

                "score_trend":
                    slope,

                "attendance_rate":
                    attendance_rate,

                "homework_rate":
                    homework_rate,

                "score_volatility":
                    score_volatility,

                "actual_next_week_score":
                    next_week_score,

                "failed_next_week":
                    failed_next_week,
            }
        )


features = pd.DataFrame(
    records
)


if features.empty:
    raise ValueError(
        "No training examples could be created."
    )


# --------------------------------------------------
# 4. MODEL VARIABLES
# --------------------------------------------------

feature_columns = [
    "recent_mean_score",
    "last_score",
    "score_trend",
    "attendance_rate",
    "homework_rate",
    "score_volatility",
]


X = features[
    feature_columns
]

y = features[
    "failed_next_week"
]


print(
    "\nNumber of training examples:",
    len(features),
)

print(
    "Number of failures:",
    int(y.sum()),
)

print(
    "Number of passes:",
    int((y == 0).sum()),
)


# --------------------------------------------------
# 5. TIME-BASED TRAIN / TEST SPLIT
# --------------------------------------------------

# Use earlier weeks to train
# Use later weeks to test

weeks_available = sorted(
    features[
        "prediction_week"
    ].unique()
)


split_index = int(
    len(weeks_available) * 0.8
)


train_weeks = weeks_available[
    :split_index
]

test_weeks = weeks_available[
    split_index:
]


train_mask = features[
    "prediction_week"
].isin(
    train_weeks
)

test_mask = features[
    "prediction_week"
].isin(
    test_weeks
)


X_train = features.loc[
    train_mask,
    feature_columns,
]

y_train = features.loc[
    train_mask,
    "failed_next_week",
]


X_test = features.loc[
    test_mask,
    feature_columns,
]

y_test = features.loc[
    test_mask,
    "failed_next_week",
]


# --------------------------------------------------
# 6. LOGISTIC REGRESSION MODEL
# --------------------------------------------------

model = Pipeline(
    [
        (
            "scaler",
            StandardScaler(),
        ),
        (
            "logistic",
            LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
            ),
        ),
    ]
)


model.fit(
    X_train,
    y_train,
)


# --------------------------------------------------
# 7. TEST MODEL
# --------------------------------------------------

test_probability = model.predict_proba(
    X_test
)[:, 1]


test_prediction = (
    test_probability >= 0.5
).astype(int)


print(
    "\nCONFUSION MATRIX"
)

print(
    confusion_matrix(
        y_test,
        test_prediction,
    )
)


print(
    "\nCLASSIFICATION REPORT"
)

print(
    classification_report(
        y_test,
        test_prediction,
        zero_division=0,
    )
)


if y_test.nunique() == 2:

    auc = roc_auc_score(
        y_test,
        test_probability,
    )

    print(
        f"ROC-AUC: {auc:.3f}"
    )


# --------------------------------------------------
# 8. CREATE WEEK 21 FEATURES
# --------------------------------------------------

week21_records = []


for student_id, student_data in math_data.groupby(
    "student_id"
):

    history = student_data[
        student_data["week"] < 21
    ].sort_values(
        "week"
    ).tail(
        LOOKBACK
    )


    if len(history) < LOOKBACK:
        continue


    recent_mean_score = (
        history[
            "score_percent"
        ].mean()
    )


    last_score = (
        history[
            "score_percent"
        ].iloc[-1]
    )


    weeks = history[
        "week"
    ].to_numpy(
        dtype=float
    )


    scores = history[
        "score_percent"
    ].to_numpy(
        dtype=float
    )


    slope, intercept = np.polyfit(
        weeks,
        scores,
        1,
    )


    attendance_rate = (
        history[
            "attendance"
        ].mean()
    )


    homework_rate = (
        history[
            "homework_completed"
        ].mean()
    )


    score_volatility = (
        history[
            "score_percent"
        ].std(
            ddof=0
        )
    )


    week21_records.append(
        {
            "student_id":
                student_id,

            "recent_mean_score":
                recent_mean_score,

            "last_score":
                last_score,

            "score_trend":
                slope,

            "attendance_rate":
                attendance_rate,

            "homework_rate":
                homework_rate,

            "score_volatility":
                score_volatility,
        }
    )


week21_data = pd.DataFrame(
    week21_records
)


# --------------------------------------------------
# 9. PREDICT WEEK 21 FAILURE PROBABILITY
# --------------------------------------------------

week21_probability = model.predict_proba(
    week21_data[
        feature_columns
    ]
)[:, 1]


week21_data[
    "failure_probability"
] = (
    week21_probability
)


week21_data[
    "failure_probability_percent"
] = (
    week21_probability
    * 100
)


week21_data[
    "predicted_fail"
] = (
    week21_probability >= 0.5
).astype(int)


# Sort highest-risk students first

week21_data = week21_data.sort_values(
    "failure_probability",
    ascending=False,
).reset_index(
    drop=True
)


# --------------------------------------------------
# 10. SAVE RESULTS
# --------------------------------------------------

week21_data.to_csv(
    OUTPUT_CSV,
    index=False,
)


print(
    f"\nPredictions saved to:"
    f"\n{Path(OUTPUT_CSV).resolve()}"
)


print(
    "\nWEEK 21 FAILURE RISK"
)


print(
    week21_data[
        [
            "student_id",
            "recent_mean_score",
            "attendance_rate",
            "homework_rate",
            "score_trend",
            "failure_probability_percent",
        ]
    ].head(20).to_string(
        index=False
    )
)


# --------------------------------------------------
# 11. GRAPH
# --------------------------------------------------

# Show 15 highest-risk students

top_risk = week21_data.head(
    15
).sort_values(
    "failure_probability_percent"
)


fig, ax = plt.subplots(
    figsize=(11, 8)
)


ax.barh(
    top_risk[
        "student_id"
    ],
    top_risk[
        "failure_probability_percent"
    ],
)


# 50% classification threshold

ax.axvline(
    50,
    linestyle="--",
    linewidth=1.5,
    label="50% classification threshold",
)


ax.set_title(
    "Week 21 Mathematics Failure Risk\n"
    "Logistic Regression Using Scores, Attendance and Homework",
    loc="left",
    fontsize=15,
)


ax.set_xlabel(
    "Predicted probability of failure (%)"
)


ax.set_ylabel(
    "Student"
)


ax.set_xlim(
    0,
    100
)


ax.grid(
    axis="x",
    alpha=0.2,
)


ax.spines[
    [
        "top",
        "right",
    ]
].set_visible(
    False
)


ax.legend(
    frameon=False
)


fig.tight_layout()


fig.savefig(
    "math_week21_failure_probability.png",
    dpi=180,
    bbox_inches="tight",
)


plt.show()
