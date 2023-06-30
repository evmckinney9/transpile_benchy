"""Depth metric for transpile_benchy using monodromy."""
from monodromy.depthPass import MonodromyDepth

from transpile_benchy.metrics.abc_metrics import MetricInterface
from transpile_benchy.passmanagers.abc_runner import CustomPassManager


class DepthMetric(MetricInterface):
    """Calculate the depth of a circuit using monodromy."""

    required_attributes = ["basis_gate"]

    def __init__(self):
        """Initialize the metric."""
        super().__init__()
        self.name = "monodromy_depth"
        self.use_geometric_mean = True

    def _get_pass(self, transpiler: CustomPassManager):
        """Return the pass associated with this metric."""
        return MonodromyDepth(transpiler.basis_gate)

    def compare_results(self, result1, result2):
        """Compare two depths.

        We might consider a depth "better" if it has a smaller value,
        hence the compare_results implementation checks if result1 is
        less than result2.
        """
        return result1 < result2


# You can add more metrics here.
# ...
