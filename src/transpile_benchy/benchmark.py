"""This is the core benchmarking class Benchmark.

It loads circuits from the submodules, applies the transpilers to them,
calculates metrics on the transpiled circuits, and plots the results.
The plots compare the metrics of the different transpilers on each
circuit.
"""
from typing import Any, List

import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit

from transpile_benchy.interface import SubmoduleInterface
from transpile_benchy.metrics import MetricInterface
from transpile_benchy.runner import AbstractRunner


class Benchmark:
    """Benchmark runner."""

    def __init__(
        self,
        transpilers: List[AbstractRunner],
        submodules: List[SubmoduleInterface],
        **kwargs,
    ):
        """Initialize benchmark runner."""
        self.transpilers = transpilers
        self.submodules = submodules
        self.metrics = []
        self.circuit_names = []
        self.results = []
        self.kwargs = kwargs

    def load_quantum_circuits(self):
        """Load Quantum Circuits from submodules."""
        return [
            qc
            for submodule in self.submodules
            for qc in submodule.get_quantum_circuits(**self.kwargs)
        ]

    def filter_circuit(self, circuit: QuantumCircuit) -> bool:
        """Filter out unwanted circuits based on their properties."""
        return circuit.depth() <= 500 and circuit.num_qubits <= 30

    def run_single_circuit(self, circuit: QuantumCircuit):
        """Run a benchmark on a single circuit."""
        self.circuit_names.append(circuit.name)
        if not self.filter_circuit(circuit):
            self.circuit_names.remove(circuit.name)
            return
        for metric in self.metrics:
            self.results[metric.name].append(self.benchmark_circuit(circuit, metric))

    def run(self, circuits=None):
        """Run benchmark."""
        if circuits is None:
            circuits = self.load_quantum_circuits()
        if isinstance(circuits, QuantumCircuit):
            self.run_single_circuit(circuits)
        else:
            for circuit in circuits:
                self.run_single_circuit(circuit)

    def benchmark_circuit(
        self, circuit: QuantumCircuit, metric: MetricInterface
    ) -> Any:
        """Benchmark a single circuit."""
        return [
            metric.calculate(transpiler.run(circuit)) for transpiler in self.transpilers
        ]

    def plot(self, save=False):
        """Plot benchmark results."""
        with plt.style.context("ipynb", "colorsblind10"):
            bar_width = 0.35
            transpiler_count = len(self.transpilers)

            for metric_name, results in self.results.items():
                plt.figure(figsize=(10, 6))
                # Create a bar for each transpiler
                for i in range(transpiler_count):
                    plt.bar(
                        np.arange(len(results)) + i * bar_width,
                        [result[i] for result in results],
                        width=bar_width,
                        label=f"Transpiler {i+1}",
                    )

                # Add labels, title, etc
                plt.xlabel("Circuit")
                plt.ylabel(metric_name)
                plt.title(f"Transpiler {metric_name} Comparison")
                max_fontsize = 10
                min_fontsize = 4
                font_size = max(min(max_fontsize, 800 // len(results)), min_fontsize)

                plt.xticks(
                    np.arange(len(results)) + bar_width * (transpiler_count - 1) / 2,
                    self.circuit_names,
                    rotation="vertical",
                    fontsize=font_size,
                )

                plt.legend()

                if save:
                    plt.savefig(f"transpile_benchy_{metric_name}.svg", dpi=300)

                # Show the plot
                plt.show()
