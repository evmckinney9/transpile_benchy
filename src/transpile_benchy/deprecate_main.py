"""Main benchmark runner."""
import glob

# from qiskit.transpiler.preset_passmanagers import level_0_pass_manager
# from qiskit import transpile
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit
from qiskit.transpiler.passmanager import PassManager
from tqdm import tqdm


class Benchmark:
    """Benchmark runner."""

    def __init__(
        self,
        *transpilers: Tuple[PassManager],
        size="small",
        prepath="../../",
        circuit_list=None,
    ):
        """Initialize benchmark runner.

        Args:
            *transpilers: Transpilers to benchmark.
        """
        self.transpilers = list(transpilers)
        self.depth_list = None
        self.circuit_names = None
        self.size = size
        self.prepath = prepath
        self.circuit_list = circuit_list

    def load_qasm_files(self):
        """Load QASM files from submodules."""
        filenames = glob.iglob(
            f"{self.prepath}/QASMBench/{self.size}/**/*.qasm", recursive=True
        )
        # # Filter out files containing '_transpiled' in their names
        filtered_filenames = list(
            filename for filename in filenames if "_transpiled" not in filename
        )

        # remove filenams that contain 'vqe' or 'bwt'
        filtered_filenames = list(
            filename
            for filename in filtered_filenames
            if "vqe" not in filename and "bwt" not in filename
        )

        filenames = glob.iglob(
            "{self.prepath}/red-queen/red_queen/games/applications/qasm/*.qasm"
        )  # noqa: E501
        # append filenames to filtered_filenames
        filtered_filenames.extend(filenames)

        # filenames = glob.iglob("../../red-queen/red_queen/games/mapping/benchmarks/misc/*.qasm")  # noqa: E501
        # # append filenames to filtered_filenames
        # filtered_filenames.extend(filenames)

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
            # remove measurements
            circuit.remove_final_measurements()
            # remove classical registers
            # circuit._clbits = []
            yield circuit

    # TODO this code is a mess
    def run(self):
        """Run benchmark."""
        if self.circuit_list is None:
            filenames = self.load_qasm_files()
            circuits = self.qiskit_circuit_generator(filenames)
        else:
            circuits = self.circuit_list
            filenames = [circuit.name for circuit in circuits]
            self.circuit_names = filenames
        self.depth_list = []

        for circuit in tqdm(circuits, total=len(filenames)):
            self.inner_depth_list = []

            if circuit.depth() > 500:
                self.circuit_names.remove(circuit.name)
                continue

            if (
                circuit.depth(
                    filter_function=lambda x: x.operation.name
                    not in ["u3", "u", "ry", "rz", "rx", "x", "y", "z", "h", "s", "t"]
                )
                > 150
            ):
                self.circuit_names.remove(circuit.name)
                continue

            # if has more than 4 qubits, reject
            if circuit.num_qubits > 30:
                self.circuit_names.remove(circuit.name)
                continue

            print(f"Running {circuit.name}")
            try:
                pass

                # XXX
                nested_depth_list = []
                circuit_list = []
                for i, transpiler in enumerate(self.transpilers):
                    best = None
                    for _ in range(10):
                        transpiled_circuit = transpiler.run(circuit)
                        circuit_list.append(transpiled_circuit)
                        # nested_depth_list.append(
                        #     transpiled_circuit.depth(
                        #         filter_function=lambda x: x.operation.name
                        #         not in ["u3", "u", "rz", "rx"]
                        #     )
                        temp = transpiled_circuit.depth(
                            filter_function=lambda x: x.operation.name
                            not in [
                                "u3",
                                "u",
                                "ry",
                                "rz",
                                "rx",
                                "x",
                                "y",
                                "z",
                                "h",
                                "s",
                                "t",
                            ]
                        )
                        if best is None or temp < best:
                            best = temp
                    nested_depth_list.append(best)

                self.inner_depth_list.extend(nested_depth_list)
                # for i, transpiled_circuit in enumerate(circuit_list):
                #     transpiled_circuit.name = f"{circuit.name}_transpiled_{i}"
                # print(transpiled_circuit.draw(fold=-1))

                # XXX

            except Exception as e:
                print(f"Error: {e}")
                self.circuit_names.remove(circuit.name)
                continue

            # remove circuits with depth > 50
            if any(depth > 200 for depth in self.inner_depth_list):
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
            min_fontsize = 4
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
