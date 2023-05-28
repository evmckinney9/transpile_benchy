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
from qiskit.transpiler.passes import Optimize1qGates, OptimizeSwapBeforeMeasure


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
        raise NotImplementedError

    @abstractmethod
    def post_process(self, circuit):
        """Post-process the circuit after running."""
        pass

    def run(self, circuit):
        """Run the transpiler on the circuit."""
        # Pre-processing
        circuit = self.pre_process(circuit)

        # Main processing
        self.main_pm.property_set = self.pre_pm.property_set
        circuit = self.main_process(circuit)

        # Post-processing
        self.post_pm.property_set = self.main_pm.property_set
        circuit = self.post_process(circuit)

        return circuit


class CustomPassManager(AbstractRunner):
    """Abstract class for a custom PassManager."""

    def pre_process(self, circuit):
        """Pre-process the circuit before running."""
        # Add pre-processing steps here
        # self.pre_pm.append(Unroller(["u", "cx", "iswap", "swap"]))
        return self.pre_pm.run(circuit)

    def post_process(self, circuit):
        """Post-process the circuit after running."""
        self.post_pm.append(
            [
                OptimizeSwapBeforeMeasure(),
                Optimize1qGates(basis=["u", "cx", "iswap", "swap"]),
                # Collect2qBlocks(),
                # ConsolidateBlocks(force_consolidate=True),
            ]
        )
        return self.post_pm.run(circuit)
