"""This file contains the MetricInterface abstract base class.

The abstract method calculate() should implement the calculation of the
metric from a given QuantumCircuit. An example metric DepthMetric is
provided.
"""
from abc import ABC, abstractmethod

from monodromy.depthPass import MonodromyDepth
from qiskit.transpiler.basepasses import AnalysisPass


class MetricInterface(ABC):
    """Abstract class for a metric."""

    @staticmethod
    @abstractmethod
    def get_pass() -> AnalysisPass:
        """Return the pass associated with this metric."""
        pass

    def __lt__(self, other: "MetricInterface") -> bool:
        """Determine if this result is better than the other result.

        By default, smaller values are considered better. Override this
        method for metrics where larger values are better.
        """
        return self.get_pass().property_set.get(
            self.name, float("inf")
        ) < other.get_pass().property_set.get(other.name, float("inf"))


class DepthMetric(MetricInterface):
    """Calculate the depth of a circuit."""

    def __init__(self, basis_gate):
        """Initialize the metric."""
        self.name = "monodromy_depth"
        self.transpiler_pass = MonodromyDepth(basis_gate=basis_gate)

    def get_pass(self):
        """Return the pass associated with this metric."""
        return self.transpiler_pass


# You can add more metrics here.
