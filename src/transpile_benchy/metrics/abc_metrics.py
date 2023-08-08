"""This file contains the MetricInterface abstract base class.

The abstract method calculate() should implement the calculation of the
metric from a given QuantumCircuit. An example metric DepthMetric is
provided.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from transpile_benchy.passmanagers.abc_runner import CustomPassManager

import inspect
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
    data: List = field(default_factory=list)

    def __repr__(self) -> str:
        """Pretty print the result."""
        return f"Result({self.metric.name}, {self.average})"

    def add_trial(self, value):
        """Add a trial result."""
        self.data.append(value)
        # NOTE, this is a workaround for when I want to save lists instead of floats
        # for example, tracking cost as function of layout restarts
        # in practice, we just keep the minimum, but I want to keep the full list
        if isinstance(value, list):
            self.trials.append(min(value))
        else:
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

        If is_lower_better is True for the metric, lower values are
        considered better.
        """
        return min(self.trials) if self.metric.is_lower_better else max(self.trials)

    @property
    def worst(self):
        """Return the worst trial result."""
        return max(self.trials) if self.metric.is_lower_better else min(self.trials)


class MetricInterface(ABC):
    """Abstract class for a metric."""

    def __init__(self, name: str, pretty_name: str = None):
        """Initialize the result metrics."""
        self.name = name
        self.pretty_name = pretty_name or name
        self.is_lower_better = True
        self.use_geometric_mean = False
        self.clear_saved_results()

    def construct_pass(self, transpiler) -> AnalysisPass:
        """Construct the pass associated with this metric.

        Check if the required attributes exist in the transpiler and
        then return the pass associated with this metric by calling the
        _construct_pass method.
        """
        required_attributes = inspect.signature(self._construct_pass).parameters.keys()
        missing_attributes = [
            attr for attr in required_attributes if not hasattr(transpiler, attr)
        ]
        if missing_attributes:
            raise ValueError(
                f"Transpiler missing these attributes: '{missing_attributes}',\
                needed to instantiate {self.name}."
            )
        attrs = {attr: transpiler.__dict__.get(attr) for attr in required_attributes}
        return self._construct_pass(**attrs)

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

    def prepare_plot_data(self, auto_sort=True):
        """Sort and parse the result dictionary for plotting."""
        result_dict = {}

        for transpiler_name, results_by_circuit in self.saved_results.items():
            for circuit_name, result in results_by_circuit.items():
                if circuit_name not in result_dict:
                    result_dict[circuit_name] = []
                result_dict[circuit_name].append((transpiler_name, result))

        if auto_sort:
            # Sort by the average result of the first transpiler
            sorted_results = sorted(
                result_dict.items(),
                key=lambda x: x[1][0][1].average,
            )
        else:
            sorted_results = result_dict.items()

        return sorted_results

    @abstractmethod
    def _construct_pass(self, **kwargs):
        """Return the pass associated with this metric."""
        raise NotImplementedError


class DoNothing(AnalysisPass):
    """A pass that does nothing.

    This is a workaround for metrics that do not require a pass. For
    example, if some other pass already calculates the metric.
    """

    def run(self, dag):
        """Do nothing."""
        return dag
