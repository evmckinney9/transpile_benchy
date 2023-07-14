"""Timer metric for transpile_benchy."""
from transpile_benchy.metrics.abc_metrics import DoNothing, MetricInterface


class TimeMetric(MetricInterface):
    """Return the total runtime of the transpiler.

    Note, since the runner already handles timing in between stages,
    this metric has no associated pass. Just need to add it to the
    runner, so that it benchmarker will access the timing information.
    """

    def __init__(self):
        """Initialize the metric."""
        super().__init__(name="total_runtime", pretty_name="Total Runtime")

    def _construct_pass(self):
        """Return the pass associated with this metric."""
        return DoNothing()
