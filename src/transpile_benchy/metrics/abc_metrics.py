"""This file contains the MetricInterface abstract base class.

The abstract method calculate() should implement the calculation of the
metric from a given QuantumCircuit. An example metric DepthMetric is
provided.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from transpile_benchy.passmanagers.abc_runner import CustomPassManager

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from statistics import mean
from typing import List

from qiskit.transpiler.basepasses import AnalysisPass
from scipy.stats.mstats import gmean


@dataclass
class Result:
    """A class to handle results of multiple trials."""

    metric: "MetricInterface"
    trials: List = field(default_factory=list)

    def add_trial(self, value):
        """Add a trial result."""
        self.trials.append(value)

    @property
    def average(self):
        """Calculate the average of the trial results."""
        if self.metric.use_geometric_mean:
            return gmean(self.trials)
        else:
            return mean(self.trials)

    @property
    def best(self):
        """Return the best trial result.

        NOTE: convention is that lower is better.
        """
        return min(self.trials, key=self.metric.compare_results)

    @property
    def worst(self):
        """Return the worst trial result."""
        return max(self.trials, key=self.metric.compare_results)


class MetricInterface(ABC):
    """Abstract class for a metric."""

    required_attributes = []  # Each subclass can override this list

    def __init__(self, name: str):
        """Initialize the result metrics."""
        self.name = name
        self.clear_saved_results()
        self.use_geometric_mean = False

    def get_pass(self, transpiler) -> AnalysisPass:
        """Return the pass associated with this metric."""
        # check if all required attributes are present in the transpiler
        for attribute in self.required_attributes:
            if not hasattr(transpiler, attribute):
                raise ValueError(
                    f"Transpiler missing '{attribute}' attr to instantiate {self.name}."
                )

        return self._get_pass(transpiler)

    def clear_saved_results(self):
        """Clear all saved results."""
        self.saved_results = {}

    def add_result(self, transpiler: CustomPassManager, circuit_name: str):
        """Add a result to the saved results.

        Args:
            transpiler (CustomPassManager): The used transpiler.
            circuit_name (str): The name of the circuit.
        """
        result = transpiler.property_set.get(self.name, None)
        if result is None:
            raise ValueError(f"Result for {self.name} not found in property set.")

        if transpiler.name not in self.saved_results:
            self.saved_results[transpiler.name] = {}

        if circuit_name not in self.saved_results[transpiler.name]:
            self.saved_results[transpiler.name][circuit_name] = Result(self)

        self.saved_results[transpiler.name][circuit_name].add_trial(result)

    def get_result(self, transpiler: CustomPassManager, circuit_name: str) -> Result:
        """Get a result from the saved results."""
        return self.saved_results[transpiler.name][circuit_name]

    @abstractmethod
    def _get_pass(self, transpiler):
        """Return the pass associated with this metric."""
        raise NotImplementedError

    # optionally override this method
    def compare_results(self, result1, result2):
        """Compare two results.

        Default assumes lower is better. Return true if result1 is
        better than result2
        """
        return result1 < result2


class DoNothing(AnalysisPass):
    """A pass that does nothing.

    This is a workaround for metrics that do not require a pass. For
    example, if some other pass already calculates the metric.
    """

    def run(self, dag):
        """Do nothing."""
        return dag
