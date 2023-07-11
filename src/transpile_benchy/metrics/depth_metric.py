"""Depth metric for transpile_benchy using monodromy."""
from monodromy.depthPass import MonodromyDepth, MonodromyTotal

from transpile_benchy.metrics.abc_metrics import MetricInterface
from transpile_benchy.passmanagers.abc_runner import CustomPassManager


class DepthMetric(MetricInterface):
    """Calculate the depth of a circuit using monodromy."""

    required_attributes = ["basis_gate", "gate_costs"]

    def __init__(self):
        """Initialize the metric."""
        super().__init__(name="monodromy_depth", pretty_name="Average Depth")
        self.use_geometric_mean = True

    def _get_pass(self, transpiler: CustomPassManager):
        """Return the pass associated with this metric."""
        return MonodromyDepth(transpiler.basis_gate, transpiler.gate_costs)


class TotalMetric(MetricInterface):
    """Calculate the total number of gates in a circuit."""

    def __init__(self):
        """Initialize the metric."""
        super().__init__(name="monodromy_total", pretty_name="Total 2Q Gates")
        self.use_geometric_mean = True

    def _get_pass(self, transpiler: CustomPassManager):
        """Return the pass associated with this metric."""
        return MonodromyTotal(transpiler.basis_gate, transpiler.gate_costs)


# You can add more metrics here.
# ...
