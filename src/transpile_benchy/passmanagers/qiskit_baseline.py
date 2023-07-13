"""Qiskit Baseline Pass Manager."""
from qiskit.circuit.library import CXGate
from qiskit.compiler import transpile
from qiskit.transpiler import PassManager

from transpile_benchy.passmanagers.abc_runner import CustomPassManager


class QiskitStage(PassManager):
    """QiskitStage uses Qiskit's built-in transpilation strategies."""

    default_basis = ["u", "cx", "id", "measure", "reset", "barrier"]
    CONFIGS = {
        1: {"optimization_level": 1, "basis_gates": default_basis},
        2: {"optimization_level": 2, "basis_gates": default_basis},
        3: {"optimization_level": 3, "basis_gates": default_basis},
    }

    def __init__(self, **transpiler_kwargs):
        """Initialize the QiskitStage."""
        self.transpiler_kwargs = transpiler_kwargs

    @classmethod
    def from_predefined_config(cls, optimization_level: int, **kwargs):
        """Create a pre-defined QiskitStage.

        Create a QiskitStage from a pre-defined transpiler configuration
        and merge it with provided kwargs.
        """
        config = cls.CONFIGS.get(optimization_level)
        if not config:
            raise ValueError(f"Invalid level. Choose from {list(cls.CONFIGS.keys())}.")
        config.update(kwargs)  # Merge predefined config with provided kwargs
        return cls(**config)

    def run(self, circuit):
        """Run the transpiler on the circuit."""
        return transpile(circuit, **self.transpiler_kwargs)


class QiskitBaseline(CustomPassManager):
    """QiskitBaseline uses Qiskit's built-in transpilation strategies."""

    def __init__(self, optimization_level: int, **transpiler_kwargs):
        """Initialize the QiskitBaseline."""
        super().__init__(name=f"Qiskit_o{optimization_level}")
        self.optimization_level = optimization_level
        self.transpiler_kwargs = transpiler_kwargs

        # required attributes for the metrics
        self.basis_gate = CXGate()
        self.gate_costs = 1.0

    def stage_builder(self):
        """Build stages in a defined sequence."""

        def _builder():
            yield QiskitStage.from_predefined_config(
                optimization_level=self.optimization_level, **self.transpiler_kwargs
            )

        return _builder
