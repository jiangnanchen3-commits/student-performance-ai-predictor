from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


CSV_FILE = "uk_school_student_data_50_students_attendance_linked.csv"

STUDENT_ID = "S001"
FORECAST_WEEK = 21
LOOKBACK = 3


# -----------------------------
# LOAD DATA
# -----------------------------

data = pd.read_csv(CSV_FILE)

data["week"] = pd.to_numeric(data["week"], errors="coerce")
data["score_percent"] = pd.to_numeric(data["score_percent"], errors="coerce")
data["attendance"] = pd.to_numeric(data["attendance"], errors="coerce")
data["homework_completed"] = pd.to_numeric(
    data["homework_completed"],
    errors="coerce",
)


# -----------------------------
# MATHEMATICS DATA ONLY
# -----------------------------

math_data = data[
    data["subject"].astype(str).str.strip().str.casefold()
    == "mathematics"
].copy()

math_history = math_data[
    math_data["week"] < FORECAST_WEEK
].dropna(
    subset=[
        "student_id",
        "week",
        "score_percent",
        "attendance",
        "homework_completed",
    ]
)


# -----------------------------
# FIT MULTIPLE REGRESSION
# USING ALL STUDENTS
# -----------------------------

X = math_history[
    [
        "week",
        "attendance",
        "homework_completed",
    ]
].to_numpy(dtype=float)

y = math_history["score_percent"].to_numpy(dtype=float)


# Add intercept
X_design = np.column_stack(
    [
        np.ones(len(X)),
        X,
    ]
)

beta, _, _, _ = np.linalg.lstsq(
    X_design,
    y,
    rcond=None,
)

intercept = beta[0]
week_beta = beta[1]
attendance_beta = beta[2]
homework_beta = beta[3]


# -----------------------------
# SELECT ONE STUDENT
# -----------------------------

student = math_history[
    math_history["student_id"] == STUDENT_ID
].copy()

student = student.sort_values("week")

if student.empty:
    raise ValueError(
        f"Student {STUDENT_ID} was not found."
    )


# -----------------------------
# RECENT ATTENDANCE + HOMEWORK
# -----------------------------

recent = student.tail(LOOKBACK)

expected_attendance = recent["attendance"].mean()

expected_homework = recent[
    "homework_completed"
].mean()


# -----------------------------
# WEEK 21 PREDICTION
# -----------------------------

predicted_score = (
    intercept
    + week_beta * FORECAST_WEEK
    + attendance_beta * expected_attendance
    + homework_beta * expected_homework
)

predicted_score = float(
    np.clip(predicted_score, 0, 100)
)


print(
    f"{STUDENT_ID} predicted Week 21 "
    f"Mathematics score: "
    f"{predicted_score:.1f}%"
)

print(
    f"Recent attendance rate: "
    f"{expected_attendance:.2f}"
)

print(
    f"Recent homework rate: "
    f"{expected_homework:.2f}"
)


# -----------------------------
# GRAPH
# -----------------------------

fig, ax = plt.subplots(
    figsize=(11, 7)
)


# Historical actual Mathematics scores
ax.plot(
    student["week"],
    student["score_percent"],
    marker="o",
    linewidth=2,
    label="Actual Mathematics score",
)


# Last actual observation
last_week = student["week"].iloc[-1]

last_score = student[
    "score_percent"
].iloc[-1]


# Connect Week 20 to Week 21 prediction
ax.plot(
    [
        last_week,
        FORECAST_WEEK,
    ],
    [
        last_score,
        predicted_score,
    ],
    linestyle="--",
    linewidth=2,
    label="Prediction",
)


# Prediction point
ax.scatter(
    FORECAST_WEEK,
    predicted_score,
    s=100,
    zorder=5,
)


# Prediction annotation
ax.annotate(
    f"Week 21 prediction\n{predicted_score:.1f}%",
    xy=(
        FORECAST_WEEK,
        predicted_score,
    ),
    xytext=(
        FORECAST_WEEK - 3,
        predicted_score + 10,
    ),
    arrowprops={
        "arrowstyle": "->",
    },
)


# Failure threshold
ax.axhline(
    40,
    linestyle="--",
    linewidth=1.5,
    label="40% failure threshold",
)


# Week 21 marker
ax.axvline(
    FORECAST_WEEK,
    linestyle=":",
    linewidth=1.2,
)


# -----------------------------
# DESIGN
# -----------------------------

ax.set_title(
    f"{STUDENT_ID} Mathematics Performance\n"
    "Week 21 Prediction Using Attendance and Homework",
    loc="left",
    fontsize=15,
)

ax.set_xlabel("Week")

ax.set_ylabel(
    "Mathematics Score (%)"
)

ax.set_ylim(0, 100)

ax.set_xticks(
    range(
        int(student["week"].min()),
        FORECAST_WEEK + 1,
    )
)

ax.grid(
    axis="y",
    alpha=0.25,
)

ax.spines[
    ["top", "right"]
].set_visible(False)

ax.legend(
    frameon=False
)

fig.tight_layout()

plt.show()

