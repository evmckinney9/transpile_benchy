"""Main benchmark runner."""
import glob

# from qiskit.transpiler.preset_passmanagers import level_0_pass_manager
# from qiskit import transpile
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit
from qiskit.transpiler.passmanager import PassManager
from tqdm.notebook import tqdm


class Benchmark:
    """Benchmark runner."""

    def __init__(self, *transpilers: Tuple[PassManager], size="small"):
        """Initialize benchmark runner.

        Args:
            *transpilers: Transpilers to benchmark.
        """
        self.transpilers = list(transpilers)
        self.depth_list = None
        self.circuit_names = None
        self.size = size

    def load_qasm_files(self):
        """Load QASM files from submodules."""
        filenames = glob.iglob(f"../../QASMBench/{self.size}/**/*.qasm", recursive=True)
        # # Filter out files containing '_transpiled' in their names
        filtered_filenames = (
            filename for filename in filenames if "_transpiled" not in filename
        )
        return filtered_filenames

    def qiskit_circuit_generator(self, filenames):
        """Return a generator for Qiskit circuits."""
        self.circuit_names = []
        for filename in filenames:
            # Load transpiled file
            circuit = QuantumCircuit.from_qasm_file(filename)
            # clean filename for circuit name
            circuit.name = filename.split("/")[-1].split(".")[0]
            self.circuit_names.append(circuit.name)
            yield circuit

    def run(self):
        """Run benchmark."""
        filenames = self.load_qasm_files()
        circuits = self.qiskit_circuit_generator(filenames)
        self.depth_list = []

        for circuit in tqdm(circuits):
            # print(f"Running {circuit.name}")
            self.inner_depth_list = []
            for i, transpiler in enumerate(self.transpilers):
                # print(f"Transpiling with transpiler {i+1}")
                # XXX should be transpiler.run() instead ?
                transpiled_circuit = transpiler(circuit)
                self.inner_depth_list.append(transpiled_circuit.depth())

            # remove circuits with depth > 50
            if any(depth > 50 for depth in self.inner_depth_list):
                self.circuit_names.remove(circuit.name)
            else:
                self.depth_list.append(self.inner_depth_list)

    def plot(self, save=False):
        """Plot benchmark results."""
        with plt.style.context("ipynb", "colorsblind10"):
            bar_width = 0.35
            transpiler_count = len(self.transpilers)

            # Create a bar for each transpiler
            for i in range(transpiler_count):
                plt.bar(
                    np.arange(len(self.depth_list)) + i * bar_width,
                    [depth[i] for depth in self.depth_list],
                    width=bar_width,
                    label=f"Transpiler {i+1}",
                )

            # Add labels, title, etc
            plt.xlabel("Circuit")
            plt.ylabel("Depth")
            plt.title("Transpiler Depth Comparison")
            max_fontsize = 10
            min_fontsize = 6
            font_size = max(
                min(max_fontsize, 800 // len(self.depth_list)), min_fontsize
            )  # noqa: E501

            plt.xticks(
                np.arange(len(self.depth_list))
                + bar_width * (transpiler_count - 1) / 2,  # noqa: E501
                self.circuit_names,
                rotation="vertical",
                fontsize=font_size,
            )

            plt.legend()

        if save:
            plt.savefig(f"transpile_benchy_{self.size}.svg", dpi=300)

        # Show the plot
        plt.show()
