"""Render module for transpile_benchy."""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator

from transpile_benchy.benchmark import Benchmark


def _plot_bars(self, metric_name, cmap, bar_width, sorted_results, ax):
    """Plot a bar for each circuit and each transpiler."""
    transpiler_count = len(self.transpilers)

    for i, (circuit_name, circuit_results) in enumerate(sorted_results):
        for j, transpiler in enumerate(self.transpilers):
            result_metrics = self.results.get_metrics(
                metric_name, circuit_name, transpiler.name
            )

            # Plot the average without label
            ax.bar(
                i * transpiler_count + j * bar_width,
                result_metrics.average,
                width=bar_width,
                color=cmap(j),
            )

            # Mark the best result
            ax.scatter(
                i * transpiler_count + j * bar_width,
                result_metrics.best,
                color="black",
                marker="*",
                s=10,
            )


def plot(benchmark: Benchmark, legend_show=True, save=False):
    """Plot benchmark results."""
    with plt.style.context(["ipynb", "colorsblind10"]):
        # LaTeX rendering
        plt.rcParams["text.usetex"] = True

        bar_width = 0.8
        transpiler_count = len(benchmark.transpilers)
        cmap = plt.cm.get_cmap("tab10", transpiler_count)

        for metric_name in benchmark.results.results.keys():
            # we are not plotting this
            if metric_name == "accepted_subs":
                continue

            # XXX temporary hard code renames
            if metric_name == "monodromy_depth":
                pretty_name = "Average Depth"

            ref_size = 1.25  # assume need .4 for legend
            if legend_show:
                fig, axs = plt.subplots(
                    2,
                    figsize=(
                        3.5,
                        ref_size + 0.4,
                    ),  # 2 inch for plot + 1 inch for legend
                    sharex=True,
                    gridspec_kw={
                        "height_ratios": [0.4, ref_size + 0.4],
                        "hspace": 0.01,
                    },  # 1:2 ratio for legend:plot
                )
                ax = axs[1]
            else:
                fig, ax = plt.subplots(
                    figsize=(3.5, ref_size)
                )  # Just 2 inch for the plot

            # Sort the data here
            sorted_results = sorted(
                list(benchmark.results.results[metric_name].items()),
                key=lambda x: list(x[1].values())[0].average,
            )

            benchmark._plot_bars(metric_name, cmap, bar_width, sorted_results, ax)

            ax.set_ylabel(pretty_name, fontsize=8)

            max_fontsize = 10
            min_fontsize = 8
            font_size = max(
                min(max_fontsize, 800 // len(sorted_results)),
                min_fontsize,
            )

            # set legend and axis font size
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

            # Create the legend in the top plot
            if legend_show:
                for j, transpiler in enumerate(benchmark.transpilers):
                    axs[0].bar(0, 0, color=cmap(j), label=f"{transpiler.name}")

                axs[0].legend(loc="center", ncol=2, fontsize=8, frameon=False)
                axs[0].axis("off")

            if save:
                plt.savefig(
                    f"transpile_benchy_{pretty_name}.svg",
                    dpi=300,
                    bbox_inches="tight",
                )

            plt.show()
