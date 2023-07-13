"""Depth and Total gate count metrics for transpile_benchy using monodromy."""
from monodromy.depthPass import MonodromyDepth, MonodromyTotal

from transpile_benchy.metrics.abc_metrics import MetricInterface


class DepthMetric(MetricInterface):
    """Calculate the depth of a circuit using monodromy."""

    def __init__(self, consolidate=True):
        """Initialize the metric."""
        super().__init__(name="monodromy_depth", pretty_name="Average Depth")
        self.use_geometric_mean = True
        self.consolidate = consolidate

    def _construct_pass(self, basis_gate, gate_costs):
        """Return the pass associated with this metric."""
        return MonodromyDepth(
            consolidate=self.consolidate, basis_gate=basis_gate, gate_cost=gate_costs
        )


class TotalMetric(MetricInterface):
    """Calculate the total number of gates in a circuit."""

    def __init__(self, consolidate=True):
        """Initialize the metric."""
        super().__init__(name="monodromy_total", pretty_name="Total 2Q Gates")
        self.use_geometric_mean = True
        self.consolidate = consolidate

    def _construct_pass(self, basis_gate, gate_costs):
        """Return the pass associated with this metric."""
        return MonodromyTotal(
            consolidate=self.consolidate, basis_gate=basis_gate, gate_cost=gate_costs
        )


# You can add more metrics here.
# ...
