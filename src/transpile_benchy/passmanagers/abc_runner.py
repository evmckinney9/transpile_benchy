"""An abstract base class for structure of a custom transpiler.

It defines the pre_process(), main_process(), and post_process() methods
which are meant to be implemented in subclasses for different types of
transpilers. The run() method is also defined here which runs the three
processing methods and returns the resulting circuit.
"""
from abc import ABC, abstractmethod

from qiskit.transpiler import PassManager

from transpile_benchy.metrics.abc_metrics import MetricInterface


class CustomPassManager(ABC):
    """Abstract class outlining the structure of a custom PassManager."""

    def __init__(self, stages=None, **kwargs):
        """Initialize the runner."""
        self.name = None
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.name = self.name or self.__class__.__name__
        self.property_set = {}
        self.stages = stages if stages else []

    def append_stage(self, stage_builder):
        """Add a new stage to the sequence."""
        self.stages.append(stage_builder)

    def append_metric_pass(self, metric: MetricInterface):
        """Append a analysis pass, using transpiler-specific configuration."""
        self.metric_passes.append(metric.get_pass(self))

    def build_metric_stage(self, **kwargs) -> PassManager:
        """Build a PassManager for metric analysis."""
        return PassManager(self.metric_passes)

    def run(self, circuit):
        """Run the transpiler on the circuit."""
        self.property_set = {}  # reset property set
        for stage_builder in self.stages:
            stage = stage_builder()
            stage.property_set = self.property_set
            circuit = stage.run(circuit)
            self.property_set.update(stage.property_set)
        return circuit


class ThreeStageRunner(CustomPassManager):
    """Abstract class outlining the structure of a custom PassManager."""

    @abstractmethod
    def build_pre_stage(self) -> PassManager:
        """Build the pre-process PassManager."""
        return PassManager()

    @abstractmethod
    def build_main_stage(self) -> PassManager:
        """Build the main-process PassManager."""
        return PassManager()

    @abstractmethod
    def build_post_stage(self) -> PassManager:
        """Build the post-process PassManager."""
        return PassManager()
