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

    def summary_statistics(
        self,
        metric: MetricInterface,
        transpiler_1: CustomPassManager,
        transpiler_2: CustomPassManager,
    ) -> dict:
        """Calculate statistics for a specific metric and two transpilers.

        Args:
            metric (MetricInterface): The metric to calculate statistics for.
            transpiler_1 (CustomPassManager): The baseline transpiler.
            transpiler_2 (CustomPassManager): The comparison transpiler.
        Returns:
            dict: A dictionary containing the summary statistics.
                - 'average_change': Average change of metric compared to baseline (%).
                - 'best_circuit': The circuit that had the best improvement.
                - 'worst_circuit': The circuit that had the worst improvement.
                - 'percent_changes': Dict mapping circuit names to % changes.
        """
        # Error checking
        try:
            assert metric in self.metrics
            assert transpiler_1 in self.transpilers and transpiler_2 in self.transpilers
        except AssertionError:
            raise ValueError("Invalid metric or transpiler")

        # Get the results as Dict[circuit_name, MetricResult]
        circuit_results_1 = metric.saved_results[transpiler_1.name]
        circuit_results_2 = metric.saved_results[transpiler_2.name]

        change_percentages = []
        percent_changes = {}

        for circuit_name, result_1 in circuit_results_1.items():
            if circuit_name in circuit_results_2:
                result_2 = circuit_results_2[circuit_name]
                change_percentage = (
                    (result_2.average - result_1.average) / result_1.average
                ) * 100
                change_percentages.append(change_percentage)
                percent_changes[circuit_name] = change_percentage

        average_change = sum(change_percentages) / len(change_percentages)

        if metric.is_lower_better:
            # If lower is better, the best circuit has the most negative change
            best_circuit = min(percent_changes, key=percent_changes.get)
            # The worst circuit has the least negative (or most positive) change
            worst_circuit = max(percent_changes, key=percent_changes.get)
        else:
            # If higher is better, the best circuit has the most positive change
            best_circuit = max(percent_changes, key=percent_changes.get)
            # The worst circuit has the least positive (or most negative) change
            worst_circuit = min(percent_changes, key=percent_changes.get)

        return {
            "average_change": average_change,
            "best_circuit": best_circuit,
            "worst_circuit": worst_circuit,
            "percent_changes": percent_changes,
        }

    # Below methods used for pretty printing results
    # print(benchmark) will print a table of results
    # FIXME, the following methods are redundant and should be consolidated
    # Metric.prepare_plot_data

    def __iter__(self):
        """Iterate over the results.

        Yields tuples in the format:
        (metric_name, transpiler_name, circuit_name, mean_result, trials)
        """
        for metric in self.metrics:
            for transpiler_name, results_by_circuit in metric.saved_results.items():
                for circuit_name, result in results_by_circuit.items():
                    yield (
                        metric.name,
                        transpiler_name,
                        circuit_name,
                        result.average,
                        result.trials,
                    )

    def __str__(self):
        """Return a string representation of the benchmark results."""
        output = []
        sorted_results = sorted(
            self, key=lambda x: (x[1], x[0], x[2])
        )  # Sort by transpiler, then by metric, then by circuit
        current_transpiler = ""
        current_metric = ""
        for (
            metric_name,
            transpiler_name,
            circuit_name,
            mean_result,
            trials,
        ) in sorted_results:
            if transpiler_name != current_transpiler:
                output.append(f"\nTranspiler: {transpiler_name}")
                current_transpiler = transpiler_name
            if metric_name != current_metric:
                output.append(f"\n  Metric: {metric_name}")
                current_metric = metric_name
            output.append(
                f"  Circuit: {circuit_name:<20} \
                    Mean result: {mean_result:<10.3f} \
                    Trials: {trials}"
            )
        return "\n".join(output)
