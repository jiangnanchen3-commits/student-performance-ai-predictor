"""Create a line graph of student scores from a school CSV file.

By default, every student is shown as a separate continuous line. Each point is
that student's mean score across all subjects for the week.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MaxNLocator


DEFAULT_CSV = "uk_school_student_data_50_students.csv"
REQUIRED_COLUMNS = {"student_id", "week", "subject", "score_percent"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot weekly scores, with one continuous line per student."
    )
    parser.add_argument(
        "csv_file",
        nargs="?",
        default=DEFAULT_CSV,
        help=f"CSV file to read (default: {DEFAULT_CSV})",
    )
    parser.add_argument(
        "--student",
        help="Optional student ID to plot, for example S001. Omit to show everyone.",
    )
    parser.add_argument(
        "--subject",
        help=(
            "Optional subject to plot, for example Mathematics. "
            "Omit to average each student's subjects for each week."
        ),
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
    data = data.dropna(
        subset=["student_id", "week", "subject", "score_percent"]
    )
    data["student_id"] = data["student_id"].astype(str)

    if data.empty:
        raise ValueError("No valid score records were found in the CSV.")

    return data


def create_graph(
    data: pd.DataFrame,
    output_path: Path,
    student_id: str | None = None,
    subject: str | None = None,
    show: bool = False,
) -> None:
    selected = data

    if student_id:
        selected = selected[
            selected["student_id"].str.casefold() == student_id.casefold()
        ]
        if selected.empty:
            available = ", ".join(sorted(data["student_id"].astype(str).unique())[:10])
            raise ValueError(
                f"Student {student_id!r} was not found. Example IDs: {available}"
            )

    if subject:
        subject_rows = selected[
            selected["subject"].astype(str).str.casefold() == subject.casefold()
        ]
        if subject_rows.empty:
            available_subjects = ", ".join(
                sorted(data["subject"].astype(str).unique())
            )
            raise ValueError(
                f"Subject {subject!r} was not found. Available subjects: "
                f"{available_subjects}"
            )
        selected = subject_rows
        subject_label = str(selected["subject"].iloc[0])
        subtitle = f"Weekly {subject_label} score"
    else:
        subtitle = "Weekly mean across all recorded subjects"

    weekly_scores = (
        selected.groupby(["student_id", "week"], as_index=False)["score_percent"]
        .mean()
        .sort_values(["student_id", "week"])
    )

    student_ids = sorted(weekly_scores["student_id"].unique())
    student_count = len(student_ids)
    colours = plt.colormaps["turbo"].resampled(max(student_count, 2))

    fig, ax = plt.subplots(figsize=(14, 9))
    for index, current_student in enumerate(student_ids):
        student_scores = weekly_scores[
            weekly_scores["student_id"] == current_student
        ]
        ax.plot(
            student_scores["week"],
            student_scores["score_percent"],
            color=colours(index),
            linewidth=1.5 if student_count > 1 else 2.4,
            alpha=0.82,
            label=current_student,
        )

    if student_id:
        title = f"Weekly scores for {student_ids[0]}"
    else:
        title = f"Weekly scores for every student ({student_count} students)"

    ax.set_title(f"{title}\n{subtitle}", loc="left", fontsize=15, pad=14)
    ax.set_xlabel("Week")
    ax.set_ylabel("Score (%)")
    ax.set_ylim(0, 100)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=12))
    ax.grid(axis="y", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    legend_columns = min(10, max(1, student_count))
    ax.legend(
        title="Student ID",
        loc="upper center",
        bbox_to_anchor=(0.5, -0.12),
        frameon=False,
        ncols=legend_columns,
        fontsize=8,
        title_fontsize=9,
    )

    fig.tight_layout(rect=(0, 0.12, 1, 1))
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
        subject=args.subject,
        show=args.show,
    )


if __name__ == "__main__":
    main()
