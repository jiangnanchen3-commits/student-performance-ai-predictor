"""Create a line graph of student scores from a school CSV file.

By default, the graph shows the mean score for each subject in each week.
Pass --student S001 to plot one student's results instead.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


DEFAULT_CSV = "uk_school_student_data_50_students.csv"
REQUIRED_COLUMNS = {"student_id", "week", "subject", "score_percent"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot weekly student scores, with one line per subject."
    )
    parser.add_argument(
        "csv_file",
        nargs="?",
        default=DEFAULT_CSV,
        help=f"CSV file to read (default: {DEFAULT_CSV})",
    )
    parser.add_argument(
        "--student",
        help="Optional student ID to plot, for example S001. Omit for school averages.",
    )
    parser.add_argument(
        "--output",
        default="student_performance_graph.png",
        help="Path for the saved graph (default: student_performance_graph.png)",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Open the graph in a window after saving it.",
    )
    return parser.parse_args()


def load_data(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path.resolve()}")

    data = pd.read_csv(csv_path)
    missing = REQUIRED_COLUMNS.difference(data.columns)
    if missing:
        raise ValueError(
            "The CSV is missing required columns: " + ", ".join(sorted(missing))
        )

    data = data.copy()
    data["week"] = pd.to_numeric(data["week"], errors="coerce")
    data["score_percent"] = pd.to_numeric(
        data["score_percent"], errors="coerce"
    )
    data = data.dropna(subset=["week", "subject", "score_percent"])

    if data.empty:
        raise ValueError("No valid score records were found in the CSV.")

    return data


def create_graph(
    data: pd.DataFrame,
    output_path: Path,
    student_id: str | None = None,
    show: bool = False,
) -> None:
    if student_id:
        selected = data[
            data["student_id"].astype(str).str.casefold() == student_id.casefold()
        ]
        if selected.empty:
            available = ", ".join(sorted(data["student_id"].astype(str).unique())[:10])
            raise ValueError(
                f"Student {student_id!r} was not found. Example IDs: {available}"
            )
        title = f"Weekly scores for {student_id.upper()}"
        subtitle = "Individual score by subject"
    else:
        selected = data
        title = "Average student score by week and subject"
        subtitle = f"Mean scores across {selected['student_id'].nunique()} students"

    weekly_scores = (
        selected.groupby(["week", "subject"], as_index=False)["score_percent"]
        .mean()
        .sort_values(["week", "subject"])
    )
    score_table = weekly_scores.pivot(
        index="week", columns="subject", values="score_percent"
    )

    fig, ax = plt.subplots(figsize=(11, 6.5))
    for subject in score_table.columns:
        ax.plot(
            score_table.index,
            score_table[subject],
            marker="o",
            linewidth=2.2,
            markersize=5,
            label=str(subject),
        )

    ax.set_title(f"{title}\n{subtitle}", loc="left", fontsize=15, pad=14)
    ax.set_xlabel("Week")
    ax.set_ylabel("Score (%)")
    ax.set_ylim(0, 100)
    ax.set_xticks(sorted(score_table.index.unique()))
    ax.grid(axis="y", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(title="Subject", frameon=False, ncols=min(3, len(score_table.columns)))

    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=180, bbox_inches="tight")
    print(f"Graph saved to: {output_path.resolve()}")

    if show:
        plt.show()
    else:
        plt.close(fig)


def main() -> None:
    args = parse_args()
    data = load_data(Path(args.csv_file))
    create_graph(
        data,
        output_path=Path(args.output),
        student_id=args.student,
        show=args.show,
    )


if __name__ == "__main__":
    main()