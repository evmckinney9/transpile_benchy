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

from transpile_benchy.library import CircuitLibrary
from transpile_benchy.metrics.abc_metrics import MetricInterface
from transpile_benchy.metrics.timer import TimeMetric
from transpile_benchy.passmanagers.abc_runner import CustomPassManager


class Benchmark:
    """Benchmark runner."""

    def __init__(
        self,
        transpilers: List[CustomPassManager],
        circuit_library: CircuitLibrary,
        metrics: List[MetricInterface] = None,
        logger: Logger = None,
        num_runs: int = 3,
    ):
        """Initialize benchmark runner."""
        self.transpilers = transpilers
        self.library = circuit_library
        self.metrics = metrics or []
        # automatically extend with TimerMetric
        self.metrics.append(TimeMetric())
        self.circuit_names = []
        self.num_runs = num_runs
        self.logger = logger

        # check that all the transpilers have different names
        if len(set([t.name for t in self.transpilers])) != len(self.transpilers):
            raise ValueError("Transpilers must have unique names")

        # give each transpiler a reference to the metrics
        for transpiler in self.transpilers:
            transpiler._clear_metrics()
            for metric in self.metrics:
                transpiler._append_metric_pass(metric)

    def _filter_circuit(self, circuit: QuantumCircuit) -> bool:
        """Filter out unwanted circuits based on their properties.

        Return True if the circuit should be included in the benchmark.
        """
        if circuit.num_qubits < 2:
            return False
        if "square_root" in circuit.name:
            return False
        return circuit.depth() <= 1200 and circuit.num_qubits <= 64

    def _try_transpilation(self, transpiler, circuit, run_index):
        """Attempt to transpile, returns transpiled circuit or raises Error."""
        if not self._filter_circuit(circuit):
            if self.logger:
                self.logger.debug(f"Skipping circuit {circuit.name} due to filtering")
            return None
        if self.logger:
            self.logger.debug(
                f"Running transpiler {transpiler.name} on circuit {circuit.name}"
            )
        try:
            # ensure that multiple runs have different rng
            # otherwise no point in running multiple times :)
            if hasattr(transpiler, "seed"):
                transpiler.seed = run_index

            transpiled_circuit = transpiler.run(circuit)
        except Exception as e:
            raise ValueError("Transpiler failed") from e
        return transpiled_circuit

    def run_single_circuit(self, circuit: QuantumCircuit):
        """Run a benchmark on a single circuit."""
        if self.logger:
            self.logger.debug(f"Running benchmark for circuit {circuit.name}")
        for transpiler in self.transpilers:
            for run_index in range(self.num_runs):
                transpiled_circuit = self._try_transpilation(
                    transpiler, circuit, run_index
                )
                if transpiled_circuit is None:
                    continue
                for metric in self.metrics:
                    metric.add_result(transpiler, transpiled_circuit.name)

    def run(self):
        """Run benchmark."""
        if self.logger:
            self.logger.info("Running benchmarks for circuits...")
        total = self.library.circuit_count()
        for circuit in tqdm(
            self.library,
            total=total,
            desc="Circuits from library",
        ):
            self.run_single_circuit(circuit)

    def _calculate_statistics(
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
                if result_1.average == 0:
                    if result_2.average == 0:  # The percentages are equal, no change
                        change_percentage = 0
                    else:  # result_1 is zero but result_2 not, ie ~infinite increase
                        change_percentage = float("inf")
                else:  # Normal case, result_1.average isn't zero
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

    def summary_statistics(self, transpiler_1, transpiler_2) -> dict:
        """Calculate statistics for all metrics between a pair of transpilers.

        Args:
            transpiler_1_name (str): Name of the first transpiler.
            transpiler_2_name (str): Name of the second transpiler.

        Returns:
            dict: A dictionary where the keys are metric names,
                and the values are calculated statistics for the corresponding metric
                between the pair of transpilers.
        """
        summary = {}

        if transpiler_1 is None or transpiler_2 is None:
            raise ValueError("One or both specified transpilers could not be found.")

        for metric in self.metrics:
            # calculate/store statistics for this metric on pair of transpilers
            stats = self._calculate_statistics(metric, transpiler_1, transpiler_2)
            summary[metric.name] = {
                "average_change": stats["average_change"],
                "best_circuit": stats["best_circuit"],
                "worst_circuit": stats["worst_circuit"],
            }

        return summary

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
        """Return a verbose string representation of the benchmark results."""
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
