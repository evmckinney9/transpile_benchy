"""QiskitInterface class.

This module contains the QiskitInterface class, which is a subclass of
SubmoduleInterface. It is intended to be used for submodules that are
written in Qiskit, and have a set of functions which return
QuantumCircuits.
"""
from typing import Callable, Dict, List, Optional, Type

from qiskit import QuantumCircuit

from transpile_benchy.interfaces.abc_interface import SubmoduleInterface
from transpile_benchy.interfaces.errors import CircuitNotFoundError
from transpile_benchy.interfaces.qiskit_circuits import available_circuits


class QiskitCircuitInterface(SubmoduleInterface):
    """Submodule for Qiskit circuits."""

    def __init__(
        self,
        num_qubits: List[int],
        filter_config: Optional[Dict[str, List[str]]] = None,
    ):
        """Initialize QiskitCircuitInterface submodule."""
        self.num_qubits = num_qubits
        self.circuit_functions = available_circuits
        super().__init__(filter_config, dynamic=True)

    def _get_all_circuits(self) -> List[str]:
        """Return a list of all possible circuits."""
        return [f"{func.__name__}" for func in self.circuit_functions]

    def _load_circuit(self, circuit_str: str, num_qubits=None) -> QuantumCircuit:
        """Load a QuantumCircuit from a string."""
        for func in self.circuit_functions:
            if func.__name__ == circuit_str:
                n = num_qubits or self.num_qubits
                temp_qc = func(n)
                temp_qc.name = f"{circuit_str}_{n}"
                return temp_qc

        raise CircuitNotFoundError(f"Circuit {circuit_str} not found.")


class QuantumCircuitFactory(SubmoduleInterface):
    """Subclass of SubmoduleInterface for generating quantum circuits.

    This class generates quantum circuits of a given type (e.g., QFT or QuantumVolume)
    for a specified set of qubit counts.

    Example usage:

    num_qubits = [8, 12, 16, 20, 24, 28, 32, 36]

    qiskit_functions_qft = QuantumCircuitFactory(QFT, num_qubits)

    qiskit_functions_qv = QuantumCircuitFactory(QuantumVolume, num_qubits)
    """

    def __init__(self, function_type: Type[Callable], num_qubits: List[int]) -> None:
        """Initialize QuantumCircuitFactory."""
        self.function_type = function_type
        self.num_qubits = num_qubits
        super().__init__()

    def _get_all_circuits(self) -> List[str]:
        """Return a list of all possible circuit names."""
        return [f"{self.function_type.__name__}_{n}" for n in self.num_qubits]

    def _load_circuit(self, circuit_str: str) -> QuantumCircuit:
        """Create a quantum circuit given the circuit name."""
        num_qubits = int(circuit_str.split("_")[-1])
        circuit = self.function_type(num_qubits)
        circuit.name = circuit_str
        return circuit
