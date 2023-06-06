"""This is the core benchmarking class Benchmark.

It loads circuits from the submodules, applies the transpilers to them,
calculates metrics on the transpiled circuits, and plots the results.
The plots compare the metrics of the different transpilers on each
circuit.
"""
from collections import defaultdict
from logging import Logger
from statistics import mean, stdev
from typing import List

import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit
from tqdm import tqdm

from transpile_benchy.interface import SubmoduleInterface
from transpile_benchy.metrics import MetricInterface
from transpile_benchy.runner import AbstractRunner


def nested_dict():
    """Create a nested defaultdict."""
    return defaultdict(lambda: defaultdict(ResultMetrics))


class ResultMetrics:
    def __init__(self):
        self.values = []
        self.best = None
        self.worst = None

    def add_result(self, result):
        self.values.append(result)
        if self.worst is None or not result < self.worst:
            self.worst = result
        if self.best is None or result < self.best:
            self.best = result

    @property
    def average(self):
        return mean(self.values)

    @property
    def stderr(self):
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

    def add_result(self, metric_name, circuit_name, transpiler_name, result):
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

    def load_quantum_circuits(self, submodule: SubmoduleInterface):
        """Load Quantum Circuits from a submodule."""
        return submodule.get_quantum_circuits()

    def _filter_circuit(self, circuit: QuantumCircuit) -> bool:
        """Filter out unwanted circuits based on their properties.

        Return True if the circuit should be included in the benchmark.
        """
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
        transpiled_circuit = transpiler.run(circuit)
        if transpiled_circuit is None:
            self.logger.debug(
                f"Skipping circuit {circuit.name} due to transpiler failure"
            )
        return transpiled_circuit

    def _calculate_and_store_metric(
        self, metric, transpiled_circuit, circuit_name, transpiler_name
    ):
        self.logger.debug(f"Calculating {metric.name} for circuit {circuit_name}")
        result = metric.calculate(transpiled_circuit)
        self.logger.info(f"Transpiler {transpiler_name}, {metric.name}: {result}")
        self.results.add_result(metric.name, circuit_name, transpiler_name, result)

    def run_single_circuit(self, circuit: QuantumCircuit):
        """Run a benchmark on a single circuit."""
        self.logger.debug(f"Running benchmark for circuit {circuit.name}")

        for transpiler in self.transpilers:
            for _ in range(self.num_runs):
                transpiled_circuit = self._try_transpilation(transpiler, circuit)
                if transpiled_circuit is None:
                    continue

                for metric in self.metrics:
                    self._calculate_and_store_metric(
                        metric, transpiled_circuit, circuit.name, transpiler.name
                    )

    def run(self):
        """Run benchmark."""
        self.logger.info("Running benchmarks for circuits...")
        for submodule in self.submodules:
            total = submodule.estimate_circuit_count()
            circuits = self.load_quantum_circuits(submodule)
            for circuit in tqdm(
                circuits,
                total=total,
                desc=f"Running circuits for {submodule.__class__.__name__}",
            ):
                self.run_single_circuit(circuit)

    def plot_bars(self, metric_name, cmap, bar_width):
        """Plot a bar for each circuit and each transpiler."""
        transpiler_count = len(self.transpilers)
        results = self.results.results[metric_name]

        for i, (circuit_name, circuit_results) in enumerate(results.items()):
            for j, transpiler in enumerate(self.transpilers):
                result_metrics = self.results.get_metrics(
                    metric_name, circuit_name, transpiler.name
                )

                # Plot the average
                plt.bar(
                    i * transpiler_count + j * bar_width,
                    result_metrics.average,
                    width=bar_width,
                    color=cmap(j),
                    # yerr=result_metrics.stderr,
                    label=f"{transpiler.name}" if i == 0 else "",
                )

                # Mark the best and worst results
                plt.plot(
                    [
                        i * transpiler_count + j * bar_width,
                        i * transpiler_count + j * bar_width,
                    ],
                    [result_metrics.best, result_metrics.worst],
                    color="red",
                    linewidth=1,
                )

                plt.scatter(
                    [
                        i * transpiler_count + j * bar_width,
                        i * transpiler_count + j * bar_width,
                    ],
                    [result_metrics.best, result_metrics.worst],
                    color="red",
                    marker=".",
                    s=10,
                )

    def plot(self, save=False):
        """Plot benchmark results."""
        with plt.style.context(["ipynb", "colorsblind10"]):
            bar_width = 0.5
            transpiler_count = len(self.transpilers)
            cmap = plt.cm.get_cmap("tab10", transpiler_count)

            # set legend and axis font size
            plt.rc("legend", fontsize=10)
            plt.rc("axes", labelsize=10)

            for metric_name in self.results.results.keys():
                plt.figure(figsize=(3.5, 2.5))
                self.plot_bars(metric_name, cmap, bar_width)

                plt.xlabel("Circuit")
                plt.ylabel(metric_name)

                max_fontsize = 10
                min_fontsize = 4
                font_size = max(
                    min(max_fontsize, 800 // len(self.results.results[metric_name])),
                    min_fontsize,
                )

                plt.xticks(
                    np.arange(len(self.results.results[metric_name])) * transpiler_count
                    + bar_width * (transpiler_count - 1) / 2,
                    self.results.results[metric_name].keys(),
                    rotation="vertical",
                    fontsize=font_size,
                )

                # make the title font size smaller
                plt.title(
                    f"Transpiler {metric_name} Comparison\nAverage of N={self.num_runs} runs",
                    fontsize=font_size,
                )

                plt.legend()

                if save:
                    plt.savefig(f"transpile_benchy_{metric_name}.svg", dpi=300)

                plt.show()
