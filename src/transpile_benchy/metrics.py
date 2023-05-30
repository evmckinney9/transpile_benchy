"""This file contains the MetricInterface abstract base class.

The abstract method calculate() should implement the calculation of the
metric from a given QuantumCircuit. An example metric DepthMetric is
provided.
"""
from abc import ABC, abstractmethod
from typing import Any

from qiskit import QuantumCircuit


class MetricInterface(ABC):
    """Abstract class for a metric."""

    @staticmethod
    @abstractmethod
    def calculate(circuit: QuantumCircuit) -> Any:
        """Calculate the metric from a given QuantumCircuit."""
        pass

    def is_better(self, old_result: Any, new_result: Any) -> bool:
        """Determine if a new result is better than the old result.

        By default, smaller values are considered better. Override this
        method for metrics where larger values are better.
        """
        return new_result < old_result


class DepthMetric(MetricInterface):
    """Calculate the depth of a circuit."""

    def __init__(self):
        """Initialize the metric."""
        self.name = "Depth"

    @staticmethod
    def calculate(circuit: QuantumCircuit) -> float:
        """Calculate the depth of a circuit."""
        exclude_gates = [
            "measure",
            "barrier",
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
        return circuit.depth(filter_function=lambda x: x[0].name not in exclude_gates)


# You can add more metrics here.
