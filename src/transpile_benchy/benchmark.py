"""This is the core benchmarking class Benchmark.

It loads circuits from the submodules, applies the transpilers to them,
calculates metrics on the transpiled circuits, and plots the results.
The plots compare the metrics of the different transpilers on each
circuit.
"""
from logging import Logger
from typing import List

import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit
from tqdm import tqdm

from transpile_benchy.interface import SubmoduleInterface
from transpile_benchy.metrics import MetricInterface
from transpile_benchy.runner import AbstractRunner


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
        self.results = {metric.name: {} for metric in self.metrics}
        self.num_runs = num_runs
        self.logger = logger

    def load_quantum_circuits(self, submodule: SubmoduleInterface):
        """Load Quantum Circuits from a submodule."""
        for qc in submodule.get_quantum_circuits():
            yield qc

    def _filter_circuit(self, circuit: QuantumCircuit) -> bool:
        """Filter out unwanted circuits based on their properties.

        Return True if the circuit should be included in the benchmark.
        """
        return circuit.depth() <= 500 and circuit.num_qubits <= 30

    def _try_transpilation(self, transpiler, circuit):
        """Attempt to transpile, returning the transpiled circuit or None."""
        if not self._filter_circuit(circuit):
            self.logger.debug(f"Skipping circuit {circuit.name} due to filtering")
            return None

        transpiler_name = transpiler.__class__.__name__
        self.logger.debug(
            f"Running transpiler {transpiler_name} on circuit {circuit.name}"
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
        """Calculate a metric and store it if it's the best result so far."""
        self.logger.debug(f"Calculating {metric.name} for circuit {circuit_name}")
        result = metric.calculate(transpiled_circuit)

        if circuit_name not in self.results[metric.name]:
            self.results[metric.name][circuit_name] = {}

        if transpiler_name not in self.results[metric.name][
            circuit_name
        ] or metric.is_better(
            self.results[metric.name][circuit_name][transpiler_name], result
        ):
            self.results[metric.name][circuit_name][transpiler_name] = result

    def run_single_circuit(self, circuit: QuantumCircuit):
        """Run a benchmark on a single circuit."""
        self.logger.debug(f"Running benchmark for circuit {circuit.name}")

        for transpiler in self.transpilers:
            for _ in range(self.num_runs):
                transpiled_circuit = self._try_transpilation(transpiler, circuit)
                if transpiled_circuit is None:
                    continue

                for metric in self.metrics:
                    transpiler_name = transpiler.__class__.__name__
                    self._calculate_and_store_metric(
                        metric, transpiled_circuit, circuit.name, transpiler_name
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

    def plot(self, save=False):
        """Plot benchmark results."""
        with plt.style.context("seaborn-darkgrid"):
            bar_width = 0.35
            transpiler_count = len(self.transpilers)

            # Define color palette (add more colors if you have more than 2 transpilers)
            colors = ["#1f77b4", "#ff7f0e"]

            # Loop over metrics
            for metric_name, results in self.results.items():
                # Create figure for each metric
                plt.figure(figsize=(10, 6))

                #
                print("here")

                # Create a bar for each circuit
                for i, (circuit_name, circuit_results) in enumerate(results.items()):
                    circuit_results = list(circuit_results.values())
                    # Create a bar for each transpiler
                    for j, transpiler_result in enumerate(circuit_results):
                        plt.bar(
                            i * transpiler_count + j * bar_width,
                            transpiler_result,
                            width=bar_width,
                            color=colors[
                                j % len(colors)
                            ],  # choose color based on transpiler index
                            label=f"{self.transpilers[j].__class__.__name__}"
                            if i == 0
                            else "",  # avoid duplicate labels
                        )

                # Add labels, title, etc
                plt.xlabel("Circuit")
                plt.ylabel(metric_name)
                # subtitle Best of N={self.num_runs} runs
                plt.title(
                    f"Transpiler {metric_name} Comparison,\
                          Best of N={self.num_runs} runs"
                )

                max_fontsize = 10
                min_fontsize = 4
                font_size = max(min(max_fontsize, 800 // len(results)), min_fontsize)

                # Set x-ticks labels once for each metric
                plt.xticks(
                    np.arange(len(results)) * transpiler_count
                    + bar_width * (transpiler_count - 1) / 2,
                    results.keys(),
                    rotation="vertical",
                    fontsize=font_size,
                )

                plt.legend()

                if save:
                    plt.savefig(f"transpile_benchy_{metric_name}.svg", dpi=300)

                # Show the plot
                plt.show()
