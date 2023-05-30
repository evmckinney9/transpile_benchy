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

    def __init__(self, name:str=None):
        """Initialize the runner.
        Args: optional string name,
        if blank will be set to the class name
        (use if you want to run multiple instances of the same runner
        e.g. with varying coupling maps)
        """
        self.name = name or self.__class__.__name__
        self.pm = PassManager()
        self.pre_process()
        self.main_process()
        self.post_process()

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
        circuit = self.pm.run(circuit)
        return circuit


class CustomPassManager(AbstractRunner, ABC):
    """Abstract subclass for AbstractRunner."""

    def __init__(self, coupling):
        """Initialize the runner."""
        self.coupling = coupling
        super().__init__()

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
