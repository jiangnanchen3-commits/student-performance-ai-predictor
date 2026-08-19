"""Create a line graph of Mathematics scores for all students."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MaxNLocator


CSV_FILE = "uk_school_student_data_50_students.csv"
OUTPUT_FILE = "math_student_performance_graph.png"


def load_data(csv_path: Path) -> pd.DataFrame:
    # Check whether the CSV exists
    if not csv_path.exists():
        raise FileNotFoundError(
            f"CSV file not found: {csv_path.resolve()}"
        )

    # Read the CSV
    data = pd.read_csv(csv_path)

    # Required columns
    required_columns = {
        "student_id",
        "week",
        "subject",
        "score_percent",
    }

    missing_columns = required_columns.difference(data.columns)

    if missing_columns:
        raise ValueError(
            "Missing columns: "
            + ", ".join(sorted(missing_columns))
        )

    # Convert week and score to numbers
    data["week"] = pd.to_numeric(
        data["week"],
        errors="coerce"
    )

    data["score_percent"] = pd.to_numeric(
        data["score_percent"],
        errors="coerce"
    )

    # Remove invalid rows
    data = data.dropna(
        subset=[
            "student_id",
            "week",
            "subject",
            "score_percent",
        ]
    )

    return data


def create_math_graph(data: pd.DataFrame) -> None:

    # Keep Mathematics rows only
    math_data = data[
        data["subject"]
        .astype(str)
        .str.strip()
        .str.casefold()
        == "mathematics"
    ].copy()

    if math_data.empty:
        raise ValueError(
            "No Mathematics records were found."
        )

    # Sort by student and week
    math_data = math_data.sort_values(
        ["student_id", "week"]
    )

    # Find all student IDs
    student_ids = sorted(
        math_data["student_id"].unique()
    )

    student_count = len(student_ids)

    # Generate colours
    colours = plt.colormaps["turbo"].resampled(
        max(student_count, 2)
    )

    # Create graph
    fig, ax = plt.subplots(figsize=(14, 9))

    for index, student in enumerate(student_ids):

        student_data = math_data[
            math_data["student_id"] == student
        ]

        ax.plot(
            student_data["week"],
            student_data["score_percent"],
            color=colours(index),
            linewidth=1.5,
            alpha=0.8,
            label=student,
        )

    # Graph title and labels
    ax.set_title(
        f"Weekly Mathematics Scores\n"
        f"{student_count} Students",
        loc="left",
        fontsize=16,
        pad=14,
    )

    ax.set_xlabel("Week")
    ax.set_ylabel("Mathematics Score (%)")

    # Scores from 0–100
    ax.set_ylim(0, 100)

    # Make week numbers integers
    ax.xaxis.set_major_locator(
        MaxNLocator(integer=True)
    )

    # Horizontal grid
    ax.grid(
        axis="y",
        alpha=0.25
    )

    # Remove top/right borders
    ax.spines[["top", "right"]].set_visible(False)

    # Student legend
    ax.legend(
        title="Student ID",
        loc="upper center",
        bbox_to_anchor=(0.5, -0.12),
        frameon=False,
        ncols=10,
        fontsize=8,
    )

    fig.tight_layout(
        rect=(0, 0.12, 1, 1)
    )

    # Save graph
    fig.savefig(
        OUTPUT_FILE,
        dpi=180,
        bbox_inches="tight",
    )

    print(
        f"Math graph saved to: "
        f"{Path(OUTPUT_FILE).resolve()}"
    )

    # Show graph
    plt.show()


def main():

    data = load_data(
        Path(CSV_FILE)
    )

    create_math_graph(data)


if __name__ == "__main__":
    main()
    """Create a line graph of Mathematics scores for all students."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MaxNLocator


CSV_FILE = "uk_school_student_data_50_students.csv"
OUTPUT_FILE = "math_student_performance_graph.png"


def load_data(csv_path: Path) -> pd.DataFrame:
    # Check whether the CSV exists
    if not csv_path.exists():
        raise FileNotFoundError(
            f"CSV file not found: {csv_path.resolve()}"
        )

    # Read the CSV
    data = pd.read_csv(csv_path)

    # Required columns
    required_columns = {
        "student_id",
        "week",
        "subject",
        "score_percent",
    }

    missing_columns = required_columns.difference(data.columns)

    if missing_columns:
        raise ValueError(
            "Missing columns: "
            + ", ".join(sorted(missing_columns))
        )

    # Convert week and score to numbers
    data["week"] = pd.to_numeric(
        data["week"],
        errors="coerce"
    )

    data["score_percent"] = pd.to_numeric(
        data["score_percent"],
        errors="coerce"
    )

    # Remove invalid rows
    data = data.dropna(
        subset=[
            "student_id",
            "week",
            "subject",
            "score_percent",
        ]
    )

    return data


def create_math_graph(data: pd.DataFrame) -> None:

    # Keep Mathematics rows only
    math_data = data[
        data["subject"]
        .astype(str)
        .str.strip()
        .str.casefold()
        == "mathematics"
    ].copy()

    if math_data.empty:
        raise ValueError(
            "No Mathematics records were found."
        )

    # Sort by student and week
    math_data = math_data.sort_values(
        ["student_id", "week"]
    )

    # Find all student IDs
    student_ids = sorted(
        math_data["student_id"].unique()
    )

    student_count = len(student_ids)

    # Generate colours
    colours = plt.colormaps["turbo"].resampled(
        max(student_count, 2)
    )

    # Create graph
    fig, ax = plt.subplots(figsize=(14, 9))

    for index, student in enumerate(student_ids):

        student_data = math_data[
            math_data["student_id"] == student
        ]

        ax.plot(
            student_data["week"],
            student_data["score_percent"],
            color=colours(index),
            linewidth=1.5,
            alpha=0.8,
            label=student,
        )

    # Graph title and labels
    ax.set_title(
        f"Weekly Mathematics Scores\n"
        f"{student_count} Students",
        loc="left",
        fontsize=16,
        pad=14,
    )

    ax.set_xlabel("Week")
    ax.set_ylabel("Mathematics Score (%)")

    # Scores from 0–100
    ax.set_ylim(0, 100)

    # Make week numbers integers
    ax.xaxis.set_major_locator(
        MaxNLocator(integer=True)
    )

    # Horizontal grid
    ax.grid(
        axis="y",
        alpha=0.25
    )

    # Remove top/right borders
    ax.spines[["top", "right"]].set_visible(False)

    # Student legend
    ax.legend(
        title="Student ID",
        loc="upper center",
        bbox_to_anchor=(0.5, -0.12),
        frameon=False,
        ncols=10,
        fontsize=8,
    )

    fig.tight_layout(
        rect=(0, 0.12, 1, 1)
    )

    # Save graph
    fig.savefig(
        OUTPUT_FILE,
        dpi=180,
        bbox_inches="tight",
    )

    print(
        f"Math graph saved to: "
        f"{Path(OUTPUT_FILE).resolve()}"
    )

    # Show graph
    plt.show()


def main():

    data = load_data(
        Path(CSV_FILE)
    )

    create_math_graph(data)


if __name__ == "__main__":
    main()
    