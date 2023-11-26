"""Render module for transpile_benchy."""

from typing import List, Tuple

import LovelyPlots.utils as lp  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np
import scienceplots  # noqa: F401
from matplotlib.colors import ListedColormap
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
    legend_offset = 0.4
    if legend_show:
        fig, axs = plt.subplots(
            2,
            figsize=(
                3.5,
                ref_size + legend_offset,
            ),  # 2 inch for plot + 1 inch for legend
            sharex=True,
            gridspec_kw={
                "height_ratios": [legend_offset, ref_size + legend_offset],
                "hspace": 0.01,
            },  # 1:2 ratio for legend:plot
        )
        ax = axs[1]
    else:
        fig, ax = plt.subplots(
            figsize=(3.5, ref_size)
        )  # Just 2 inch for the plot
    return fig, ax


def _plot_bars(
    ax: Axes,
    cmap,
    sorted_results: list,
    transpiler_count: int,
    bar_width: float,
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

            # # Mark the best result
            # ax.scatter(
            #     i * transpiler_count + j * bar_width,
            #     result.best,
            #     color="black",
            #     marker="*",
            #     s=10,
            # )


def _plot_trendline(
    ax: Axes, cmap, sorted_results: list, transpiler_count: int
) -> None:
    """Plot a trendline for each circuit and each transpiler."""
    for j in range(transpiler_count):
        # Gather data for this transpiler across all circuits
        x_data = [i for i in range(len(sorted_results))]
        y_data = [v[j][1].average for k, v in sorted_results]

        # Plot the data as a scatter plot
        ax.scatter(x_data, y_data, color=cmap(j))

        # Fit a line to the data and plot the line
        coeff = np.polyfit(x_data, y_data, 2)
        line = np.poly1d(coeff)(x_data)
        ax.plot(x_data, line, color=cmap(j), linestyle="dashed")


def _plot_legend(
    axs: Axes, metric: MetricInterface, cmap, override_legend=None
) -> None:
    """Plot the legend on the given axes."""
    for j, transpiler_name in enumerate(metric.saved_results.keys()):
        if override_legend is not None:
            transpiler_name = override_legend[j]
        axs[0].bar(0, 0, color=cmap(j), label=f"{transpiler_name}")

    axs[0].legend(
        loc="upper center",
        ncol=2,
        fontsize=8,
        frameon=False,
        bbox_to_anchor=(0.5, 1.5),  # 1.10
    )
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
    plot_type: str,
) -> None:
    """Configure the x-axis and y-axis of the plot."""
    ax.set_ylabel(y_label, fontsize=8)

    max_fontsize = 10
    min_fontsize = 8
    max(
        min(max_fontsize, 800 // len(sorted_results)),
        min_fontsize,
    )

    plt.rc("legend", fontsize=8)
    plt.rc("axes", labelsize=10)

    if plot_type == "bar":
        ax.set_xticks(
            np.arange(len(sorted_results)) * transpiler_count
            + bar_width * (transpiler_count - 1) / 2,
        )
    elif plot_type == "trendline":
        ax.set_xticks(np.arange(len(sorted_results)))

    ax.set_xticklabels(
        [x[0] for x in sorted_results],  # Use sorted keys
        rotation=30,
        ha="right",
        fontsize=7,
    )

    # Ensure y-axis has at least two ticks
    ax.yaxis.set_major_locator(MaxNLocator(nbins=5))

    # Set the y-axis tick labels to use fixed point notation
    ax.ticklabel_format(axis="y", style="plain")


# ===========================
# Plot Creation
# ===========================
def plot_benchmark(
    benchmark: Benchmark,
    legend_show: bool = True,
    save: bool = False,
    filename: str = "",
    plot_type: str = "bar",
    override_legend: List[str] = None,
    color_override: List[int] = None,
    auto_sort=True,
    fixed_bar_width=1.8,
) -> None:
    """Plot benchmark results."""
    with plt.style.context(["ieee"]):
        plt.rcParams["text.usetex"] = True

        for m, metric in enumerate(benchmark.metrics):
            if legend_show and m == 0:
                legend_show = True
            else:
                legend_show = False

            if metric.name == "accepted_subs":
                continue  # We are not plotting this

            fig, ax = _initialize_plot(legend_show)

            # XXX manually adjust as needed
            # Adjust bar width according to number of transpilers
            transpiler_count = len(metric.saved_results.keys())
            bar_width = fixed_bar_width / transpiler_count  # 3

            cmap = plt.cm.get_cmap("tab10", 10)  # transpiler_count)
            if color_override is not None:
                assert transpiler_count == len(color_override)
                # set cmap to use indices from color_override
                # e.g. if [0,3] then cmap(0) := cmap(0) and cmap(1) := cmap(3)
                colors = [cmap(i) for i in color_override]
                cmap = ListedColormap(colors)

            sorted_results = metric.prepare_plot_data(auto_sort)

            if plot_type == "bar":
                _plot_bars(
                    ax, cmap, sorted_results, transpiler_count, bar_width
                )
                _configure_plot(
                    ax,
                    metric.pretty_name,
                    sorted_results,
                    transpiler_count,
                    bar_width,
                    "bar",
                )
            elif plot_type == "trendline":
                _plot_trendline(ax, cmap, sorted_results, transpiler_count)
                _configure_plot(
                    ax,
                    metric.pretty_name,
                    sorted_results,
                    transpiler_count,
                    bar_width,
                    "trendline",
                )

            if legend_show:
                _plot_legend(fig.axes, metric, cmap, override_legend)

            plt.show()

            if (
                save
                and metric == benchmark.metrics[0]
                or metric == benchmark.metrics[1]
            ):
                # # fig.savefig(f"{metric.name}_benchmark.svg", dpi=300)
                # fig.savefig(f"{filename}_{metric.name}_benchmark.svg", dpi=300)
                # save fig with no cropping
                fig.savefig(
                    f"{filename}_{metric.name}_benchmark.pdf",
                    bbox_inches="tight",
                    pad_inches=0,
                )
                # fig.savefig(f"{filename}_{metric.name}_benchmark.pdf")
