"""Write summary tables to CSV and render bar charts to JPG."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def write_csv(df: pd.DataFrame, path: str | Path) -> Path:
    """Write *df* to a CSV file and return the resolved path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path.resolve()


def write_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    path: str | Path,
    *,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    figsize: tuple[int, int] = (10, 6),
) -> Path:
    """Render a bar chart from *df* and save it as a JPG."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=figsize)
    ax.bar(df[x], df[y])
    ax.set_title(title)
    ax.set_xlabel(xlabel or x)
    ax.set_ylabel(ylabel or y)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    fig.savefig(path, format="jpeg", dpi=150)
    plt.close(fig)
    return path.resolve()
