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
    """Abstract class outlining the structure of a custom PassManager.

    It uses a builder pattern for the stages so that the stages can be
    built and run in sequence, with each stage having access to the
    properties set by the previous stage. This is particularly useful
    for cases where properties set by one stage are needed for the
    construction of a later stage. For instance, the post_layout
    property set by a layout stage could be used for the construction of
    a routing stage. Note that if we were to integrate our custom pass
    more directly into existing Qiskit architecture, we might handle
    this differently.
    """

    def __init__(self, name=None):
        """Initialize the runner."""
        self.name = name or self.__class__.__name__
        self.property_set = {}
        self.metric_passes = PassManager()
        self.stages_builder = self.stage_builder()

    def stage_builder(self):
        """Override this method to define the builder function for stages."""
        raise NotImplementedError
        # def _builder():
        #     yield PassManager()  # dummy stage
        # return _builder

    def _clear_metrics(self):
        """Clear the metrics from the transpiler."""
        self.metric_passes = PassManager()

    def _append_metric_pass(self, metric: MetricInterface):
        """Append a analysis pass, using transpiler-specific configuration."""
        self.metric_passes.append(metric.construct_pass(self))

    def run(self, circuit):
        """Run the transpiler on the circuit."""
        self.property_set = {}  # reset property set
        for stage in self.stages_builder():
            stage.property_set = self.property_set
            circuit = stage.run(circuit)
            self.property_set.update(stage.property_set)

        # run metrics
        self.metric_passes.property_set = self.property_set
        self.metric_passes.run(circuit)
        self.property_set.update(self.metric_passes.property_set)
        return circuit


class ThreeStageRunner(CustomPassManager):
    """ThreeStageRunner is a PassManager that runs three stages."""

    def __init__(self, name=None):
        """Initialize the runner."""
        super().__init__(name)

    def stage_builder(self):
        """Build stages in a defined sequence."""

        def _builder():
            yield self.build_pre_stage()
            yield self.build_main_stage()
            yield self.build_post_stage()

        return _builder

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
