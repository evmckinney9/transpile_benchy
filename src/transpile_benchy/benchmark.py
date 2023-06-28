"""This is the core benchmarking class Benchmark.

It loads circuits from the submodules, applies the transpilers to them,
calculates metrics on the transpiled circuits, and plots the results.
The plots compare the metrics of the different transpilers on each
circuit.
"""
from collections import defaultdict
from logging import Logger
from statistics import geometric_mean, stdev
from typing import List

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator
from qiskit import QuantumCircuit
from tqdm import tqdm

from transpile_benchy.interface import SubmoduleInterface
from transpile_benchy.metrics import MetricInterface
from transpile_benchy.runner import AbstractRunner


def nested_dict():
    """Create a nested defaultdict."""
    return defaultdict(lambda: defaultdict(ResultMetrics))


class ResultMetrics:
    def __init__(self, use_gmean=False):
        self.values = []
        self.best = None
        self.worst = None
        self.use_gmean = use_gmean

    def __lt__(self, other):
        return self.average < other.average

    def add_result(self, result):
        self.values.append(result)
        if self.worst is None or not result < self.worst:
            self.worst = result
        if self.best is None or result < self.best:
            self.best = result

    @property
    def average(self):
        if self.use_gmean:
            return self.gmean()
        return self.mean()

    def mean(self):
        if len(self.values) == 0:
            return 0
        return sum(self.values) / len(self.values)

    def gmean(self):
        if len(self.values) == 0:
            return 0
        return geometric_mean(self.values)

    @property
    def stderr(self):
        if len(self.values) == 0:
            return 0
        return stdev(self.values) if len(self.values) > 1 else 0


class ResultContainer:
    def __init__(self):
        self.results = defaultdict(nested_dict)

    def __str__(self):
        output = []
        for metric_name, circuit_dict in self.results.items():
            for circuit_name, transpiler_dict in circuit_dict.items():
                for transpiler_name, result_metrics in transpiler_dict.items():
                    output.append(
                        f"Metric: {metric_name}, Circuit: {circuit_name}, Transpiler: {transpiler_name}"
                    )
                    output.append(f"  Best result: {result_metrics.best}")
                    output.append(f"  Worst result: {result_metrics.worst}")
                    output.append(f"  Average result: {result_metrics.average:.2f}")
                    output.append(f"  Standard error: {result_metrics.stderr:.2f}")
        return "\n".join(output)

    # TODO fix this
    def add_result(self, metric_name, circuit_name, transpiler_name, result):
        # Check the metric name and set the use_gmean attribute
        if metric_name == "monodromy_depth":
            self.results[metric_name][circuit_name][transpiler_name].use_gmean = True
        elif metric_name == "accepted_subs":
            self.results[metric_name][circuit_name][transpiler_name].use_gmean = False
        else:
            raise ValueError(f"Unknown metric name {metric_name}")

        self.results[metric_name][circuit_name][transpiler_name].add_result(result)

    def get_metrics(self, metric_name, circuit_name, transpiler_name):
        return self.results[metric_name][circuit_name][transpiler_name]

    def __iter__(self):
        """Iterator over the results in the form (metric_name, circuit_name,
        transpiler_name, result_metrics)"""
        for metric_name, circuit_dict in self.results.items():
            for circuit_name, transpiler_dict in circuit_dict.items():
                for transpiler_name, result_metrics in transpiler_dict.items():
                    yield metric_name, circuit_name, transpiler_name, result_metrics


class Benchmark:
    """Benchmark runner."""

    def __init__(
        self,
        transpilers: List[AbstractRunner],
        submodules: List[SubmoduleInterface],
        metrics: List[MetricInterface],
        logger: Logger = None,
        num_runs: int = 3,
    ):
        """Initialize benchmark runner."""
        self.transpilers = transpilers
        self.submodules = submodules
        self.metrics = metrics
        self.circuit_names = []
        self.results = ResultContainer()
        self.num_runs = num_runs
        self.logger = logger

        # check that all the transpilers have different names
        if len(set([t.name for t in self.transpilers])) != len(self.transpilers):
            raise ValueError("Transpilers must have unique names")

        # NOTE, breaking change -
        # when monodromydepth needs different basis gates, we don't want to append
        # the runner already has depth being calculated where variable basis gate is passed in

        # for metric in self.metrics:
        #     for transpiler in self.transpilers:
        #         transpiler.append_pass(metric.get_pass())

    def load_quantum_circuits(self, submodule: SubmoduleInterface):
        """Load Quantum Circuits from a submodule."""
        return submodule.get_quantum_circuits()

    def _filter_circuit(self, circuit: QuantumCircuit) -> bool:
        """Filter out unwanted circuits based on their properties.

        Return True if the circuit should be included in the benchmark.
        """
        if circuit.num_qubits < 2:
            return False
        if "square_root" in circuit.name:
            return False
        return circuit.depth() <= 800 and circuit.num_qubits <= 36

    def _try_transpilation(self, transpiler, circuit):
        """Attempt to transpile, returning the transpiled circuit or None."""
        if not self._filter_circuit(circuit):
            self.logger.debug(f"Skipping circuit {circuit.name} due to filtering")
            return None

        self.logger.debug(
            f"Running transpiler {transpiler.name} on circuit {circuit.name}"
        )
        transpiler.reset()
        transpiled_circuit = transpiler.run(circuit)
        if transpiled_circuit is None:
            self.logger.debug(
                f"Skipping circuit {circuit.name} due to transpiler failure"
            )
        return transpiled_circuit

    def _calculate_and_store_metric(self, metric, circuit_name, transpiler):
        # self.logger.debug(f"Retrieving {metric.name} for circuit {circuit_name}")
        result = transpiler.pm.property_set.get(metric.name)
        if result is None:
            self.logger.warning(
                f"No result found for {metric.name} on circuit {circuit_name} with transpiler {transpiler.name}"
            )
            return
        self.logger.info(f"Transpiler {transpiler.name}, {circuit_name}: {result}")
        self.results.add_result(metric.name, circuit_name, transpiler.name, result)

    def run_single_circuit(self, circuit: QuantumCircuit):
        """Run a benchmark on a single circuit."""
        self.logger.debug(f"Running benchmark for circuit {circuit.name}")

        for transpiler in self.transpilers:
            for _ in range(self.num_runs):
                transpiled_circuit = self._try_transpilation(transpiler, circuit)
                if transpiled_circuit is None:
                    continue

                for metric in self.metrics:
                    self._calculate_and_store_metric(metric, circuit.name, transpiler)

    def run(self):
        """Run benchmark."""
        self.logger.info("Running benchmarks for circuits...")
        for submodule in self.submodules:
            total = submodule.circuit_count()
            circuits = self.load_quantum_circuits(submodule)
            for circuit in tqdm(
                circuits,
                total=total,
                desc=f"Running circuits for {submodule.__class__.__name__}",
            ):
                self.run_single_circuit(circuit)

        # for some unknown reason have to clean out garbage keys from results
        # I think this has to do with the default dict
        # WARNING HORRIBLE HACK CODE
        for metric in self.metrics:
            for key in list(self.results.results[metric.name].keys()):
                for transpiler in self.transpilers:
                    if transpiler.name not in self.results.results[metric.name][key]:
                        self.results.results[metric.name].pop(key)

    def plot_bars(self, metric_name, cmap, bar_width, sorted_results, ax):
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

    def plot(self, legend_show=True, save=False):
        """Plot benchmark results."""
        with plt.style.context(["ipynb", "colorsblind10"]):
            # LaTeX rendering
            plt.rcParams["text.usetex"] = True

            bar_width = 0.8
            transpiler_count = len(self.transpilers)
            cmap = plt.cm.get_cmap("tab10", transpiler_count)

            for metric_name in self.results.results.keys():
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
                    list(self.results.results[metric_name].items()),
                    key=lambda x: list(x[1].values())[0].average,
                )

                self.plot_bars(metric_name, cmap, bar_width, sorted_results, ax)

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
                    for j, transpiler in enumerate(self.transpilers):
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
