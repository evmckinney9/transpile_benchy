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
    """Abstract base class for a custom PassManager."""

    def __init__(self):
        """Initialize the runner."""
        self.pm = PassManager()

    @abstractmethod
    def pre_process(self):
        """Pre-process the circuit before running.

        Append passes to self.pm here.
        """
        pass

    @abstractmethod
    def main_process(self):
        """Process the circuit.

        Append passes to self.pm here.
        """
        pass

    @abstractmethod
    def post_process(self):
        """Post-process the circuit after running.

        Append passes to self.pm here.
        """
        pass

    def run(self, circuit):
        """Run the transpiler on the circuit."""
        circuit = self.pm(circuit)
        return circuit


class CustomPassManager(AbstractRunner, ABC):
    """Abstract subclass for AbstractRunner."""

    def __init__(self, coupling):
        """Initialize the runner."""
        super().__init__()
        self.coupling = coupling

    def pre_process(self):
        """Pre-process the circuit before running."""
        # self.pm.append(Unroller(["u", "cx", "iswap", "swap"]))
        pass

    def post_process(self):
        """Post-process the circuit after running."""
        self.pm.append(
            [
                OptimizeSwapBeforeMeasure(),
                Optimize1qGates(basis=["u", "cx", "iswap", "swap"]),
                # Collect2qBlocks(),
                # ConsolidateBlocks(force_consolidate=True),
                # RootiSwapWeylDecomposition(),
            ]
        )

    @abstractmethod
    def main_process(self):
        """Abstract method for main processing."""
        pass
