"""This is the core benchmarking class Benchmark.

It loads circuits from the submodules, applies the transpilers to them,
calculates metrics on the transpiled circuits, and plots the results.
The plots compare the metrics of the different transpilers on each
circuit.
"""
from logging import Logger
from typing import List

from qiskit import QuantumCircuit
from tqdm import tqdm

from transpile_benchy.interfaces.abc_interface import SubmoduleInterface
from transpile_benchy.metrics.abc_metrics import MetricInterface
from transpile_benchy.passmanagers.abc_runner import CustomPassManager


class Benchmark:
    """Benchmark runner."""

    def __init__(
        self,
        transpilers: List[CustomPassManager],
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
        self.num_runs = num_runs
        self.logger = logger

        # check that all the transpilers have different names
        if len(set([t.name for t in self.transpilers])) != len(self.transpilers):
            raise ValueError("Transpilers must have unique names")

        # give each transpiler a reference to the metrics
        for metric in self.metrics:
            for transpiler in self.transpilers:
                transpiler.append_metric_pass(metric)

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
        """Attempt to transpile, returns transpiled circuit or raises Error."""
        if not self._filter_circuit(circuit):
            self.logger.debug(f"Skipping circuit {circuit.name} due to filtering")
            return None

        self.logger.debug(
            f"Running transpiler {transpiler.name} on circuit {circuit.name}"
        )
        try:
            transpiled_circuit = transpiler.run(circuit)
        except Exception as e:
            raise ValueError("Transpiler failed") from e
        return transpiled_circuit

    def run_single_circuit(self, circuit: QuantumCircuit):
        """Run a benchmark on a single circuit."""
        self.logger.debug(f"Running benchmark for circuit {circuit.name}")
        for transpiler in self.transpilers:
            for _ in range(self.num_runs):
                transpiled_circuit = self._try_transpilation(transpiler, circuit)
                for metric in self.metrics:
                    metric.add_result(transpiler, transpiled_circuit.name)

    def run(self):
        """Run benchmark."""
        self.logger.info("Running benchmarks for circuits...")
        for submodule in self.submodules:
            total = submodule.circuit_count()
            circuit_iterator = submodule.get_quantum_circuits()
            for circuit in tqdm(
                circuit_iterator,
                total=total,
                desc=f"Running circuits for {submodule.__class__.__name__}",
            ):
                self.run_single_circuit(circuit)

    # FIXME
    def __iter__(self):
        """Iterate over the results.

        (metric_name, circuit_name, transpiler_name, result_metrics)?
        """
        for metric in self.metrics:
            yield metric.name, metric.saved_results
