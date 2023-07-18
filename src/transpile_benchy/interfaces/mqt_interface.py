"""MQTBench submodule interface."""
from typing import Dict, List, Optional

from mqt.bench.benchmark_generator import get_benchmark
from mqt.bench.utils import get_supported_benchmarks
from qiskit import QuantumCircuit

from transpile_benchy.interfaces.abc_interface import SubmoduleInterface
from transpile_benchy.interfaces.errors import CircuitNotFoundError


class MQTBench(SubmoduleInterface):
    """Submodule for MQTBench circuits."""

    def __init__(
        self, num_qubits: int, filter_config: Optional[Dict[str, List[str]]] = None
    ) -> None:
        """Initialize MQTBench submodule."""
        self.num_qubits = num_qubits
        if filter_config is None:
            filter_config = {}
        exclude_circuits = filter_config.setdefault("exclude", [])
        exclude_circuits += ["shor", "groundstate"]
        super().__init__(filter_config, dynamic=True)

    def _get_all_circuits(self) -> List[str]:
        """Return a list of all possible circuits.

        NOTE: these names don't have num_qubits suffix.
        """
        return get_supported_benchmarks()

    def _load_circuit(self, circuit_str: str, num_qubits=None) -> QuantumCircuit:
        """Load a QuantumCircuit from a string."""
        try:
            n = num_qubits or self.num_qubits
            qc = get_benchmark(
                benchmark_name=circuit_str,
                level="alg",
                circuit_size=n,
            )
            qc.name = f"{circuit_str}_{n}"
            return qc
        except Exception as e:
            raise CircuitNotFoundError(f"Failed to load {circuit_str}: {e}")
