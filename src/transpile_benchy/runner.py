"""An abstract base class for structure of a custom transpiler.

It defines the pre_process(), main_process(), and post_process() methods
which are meant to be implemented in subclasses for different types of
transpilers. The run() method is also defined here which runs the three
processing methods and returns the resulting circuit. An example class
CustomPassManager is provided which is a custom transpiler that outlines
the structure of the main processing method.
"""
from abc import ABC, abstractmethod

from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import (
    Collect2qBlocks,
    ConsolidateBlocks,
    Optimize1qGates,
    OptimizeSwapBeforeMeasure,
    Unroller,
)


class AbstractRunner(ABC):
    """Abstract class for a custom PassManager."""

    def __init__(self):
        """Initialize the runner."""
        self.pre_pm = PassManager()
        self.main_pm = PassManager()
        self.post_pm = PassManager()

    @abstractmethod
    def pre_process(self, circuit):
        """Pre-process the circuit before running."""
        pass

    @abstractmethod
    def main_process(self, circuit):
        """Process the circuit."""
        pass

    @abstractmethod
    def post_process(self, circuit):
        """Post-process the circuit after running."""
        pass

    def run(self, circuit):
        """Run the transpiler on the circuit."""
        # Pre-processing
        circuit = self.pre_process(circuit)

        # Main processing
        circuit = self.main_process(circuit)

        # Post-processing
        circuit = self.post_process(circuit)

        # Combine property sets
        for prop in self.pre_pm.property_set.keys():
            self.main_pm.property_set[prop] = self.pre_pm.property_set[prop]
        for prop in self.post_pm.property_set.keys():
            self.main_pm.property_set[prop] = self.post_pm.property_set[prop]

        return circuit


class CustomPassManager(AbstractRunner):
    """Abstract class for a custom PassManager."""

    def pre_process(self, circuit):
        """Pre-process the circuit before running."""
        # Add pre-processing steps here
        self.pre_pm.append(Unroller(["u", "cx", "iswap", "swap"]))
        return self.pre_pm.run(circuit)

    def main_process(self, circuit):
        """Process the circuit."""
        # This method needs to be implemented by subclasses
        raise NotImplementedError

    def post_process(self, circuit):
        """Post-process the circuit after running."""
        self.post_pm.append(
            [
                OptimizeSwapBeforeMeasure(),
                Optimize1qGates(basis=["u", "cx", "iswap", "swap"]),
                Collect2qBlocks(),
                ConsolidateBlocks(force_consolidate=True),
            ]
        )
        return self.post_pm.run(circuit)
