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
    ):
        """Initialize benchmark runner."""
        self.transpilers = transpilers
        self.submodules = submodules
        self.metrics = metrics
        self.circuit_names = []
        self.results = {metric.name: {} for metric in self.metrics}
        self.logger = logger

    def load_quantum_circuits(self, submodule: SubmoduleInterface):
        """Load Quantum Circuits from a submodule."""
        for qc in submodule.get_quantum_circuits():
            yield qc

    def filter_circuit(self, circuit: QuantumCircuit) -> bool:
        """Filter out unwanted circuits based on their properties."""
        return circuit.depth() <= 500 and circuit.num_qubits <= 30

    def run_single_circuit(self, circuit: QuantumCircuit):
        """Run a benchmark on a single circuit."""
        if not self.filter_circuit(circuit):
            self.logger.debug(f"Skipping circuit {circuit.name} due to filtering")
            return
        self.logger.debug(f"Running benchmark for circuit {circuit.name}")

        for transpiler in self.transpilers:
            self.logger.debug(
                f"Running transpiler {transpiler.__class__.__name__} \
                    on circuit {circuit.name}"
            )
            transpiled_circuit = transpiler.run(circuit)
            
            if transpiled_circuit is None:
                self.logger.debug(
                    f"Skipping circuit {circuit.name} due to transpiler failure"
                )
                continue

            for metric in self.metrics:
                self.logger.debug(
                    f"Calculating {metric.name} for circuit {circuit.name}"
                )
                result = metric.calculate(transpiled_circuit)
                if circuit.name not in self.results[metric.name]:
                    self.results[metric.name][circuit.name] = []
                self.results[metric.name][circuit.name].append(result)

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

                # Create a bar for each circuit
                for i, (circuit_name, circuit_results) in enumerate(results.items()):
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
                plt.title(f"Transpiler {metric_name} Comparison")

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
