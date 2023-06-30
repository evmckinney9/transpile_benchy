"""Render module for transpile_benchy."""

from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Axes, Figure
from matplotlib.ticker import MaxNLocator

from transpile_benchy.benchmark import Benchmark
from transpile_benchy.metrics.abc_metrics import MetricInterface


# ===========================
# Plot Initialization
# ===========================
def _initialize_plot(legend_show: bool) -> Tuple[Figure, Axes]:
    """Initialize the plot and returns the fig and ax."""
    ref_size = 1.25  # Assume need .4 for legend
    if legend_show:
        fig, axs = plt.subplots(
            2,
            figsize=(3.5, ref_size + 0.4),  # 2 inch for plot + 1 inch for legend
            sharex=True,
            gridspec_kw={
                "height_ratios": [0.4, ref_size + 0.4],
                "hspace": 0.01,
            },  # 1:2 ratio for legend:plot
        )
        ax = axs[1]
    else:
        fig, ax = plt.subplots(figsize=(3.5, ref_size))  # Just 2 inch for the plot
    return fig, ax


def _plot_bars(
    ax: Axes, cmap, sorted_results: list, transpiler_count: int, bar_width: float
) -> None:
    """Plot a bar for each circuit and each transpiler."""
    for i, (circuit_name, circuit_results) in enumerate(sorted_results):
        for j, (transpiler_name, result) in enumerate(circuit_results):
            # Plot the average without label
            ax.bar(
                i * transpiler_count + j * bar_width,
                result.average,
                width=bar_width,
                color=cmap(j),
            )

            # Mark the best result
            ax.scatter(
                i * transpiler_count + j * bar_width,
                result.best,
                color="black",
                marker="*",
                s=10,
            )


def _plot_legend(axs: Axes, metric: MetricInterface, cmap) -> None:
    """Plot the legend on the given axes."""
    for j, transpiler_name in enumerate(metric.saved_results.keys()):
        axs[0].bar(0, 0, color=cmap(j), label=f"{transpiler_name}")

    axs[0].legend(loc="center", ncol=2, fontsize=8, frameon=False)
    axs[0].axis("off")


# ===========================
# Plot Customization
# ===========================
def _configure_plot(
    ax: Axes,
    y_label: str,
    sorted_results: list,
    transpiler_count: int,
    bar_width: float,
) -> None:
    """Configure the x-axis and y-axis of the plot."""
    ax.set_ylabel(y_label, fontsize=8)

    max_fontsize = 10
    min_fontsize = 8
    font_size = max(
        min(max_fontsize, 800 // len(sorted_results)),
        min_fontsize,
    )

    plt.rc("legend", fontsize=8)
    plt.rc("axes", labelsize=10)

    ax.set_xticks(
        np.arange(len(sorted_results)) * transpiler_count
        + bar_width * (transpiler_count - 1) / 2,
    )
    ax.set_xticklabels(
        [x[0] for x in sorted_results],  # Use sorted keys
        rotation=30,
        ha="right",
        fontsize=font_size,
    )

    # Ensure y-axis has at least two ticks
    ax.yaxis.set_major_locator(MaxNLocator(nbins=3))

    # Set the y-axis tick labels to use fixed point notation
    ax.ticklabel_format(axis="y", style="plain")


# ===========================
# Plot Creation
# ===========================
def plot_benchmark(
    benchmark: Benchmark, legend_show: bool = True, save: bool = False
) -> None:
    """Plot benchmark results."""
    with plt.style.context(["ipynb", "colorsblind10"]):
        plt.rcParams["text.usetex"] = True

        for metric in benchmark.metrics:
            if metric.name == "accepted_subs":
                continue  # We are not plotting this

            fig, ax = _initialize_plot(legend_show)

            # Adjust bar width according to number of transpilers
            transpiler_count = len(metric.saved_results.keys())
            bar_width = 3 / transpiler_count
            cmap = plt.cm.get_cmap("tab10", transpiler_count)

            sorted_results = metric.prepare_plot_data()
            _plot_bars(ax, cmap, sorted_results, transpiler_count, bar_width)

            _configure_plot(
                ax, metric.pretty_name, sorted_results, transpiler_count, bar_width
            )

            if legend_show:
                _plot_legend(fig.axes, metric, cmap)

            plt.show()

            if save:
                fig.savefig(f"{metric.name}_benchmark.svg", dpi=300)
