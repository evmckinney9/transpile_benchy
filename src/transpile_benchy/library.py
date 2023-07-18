"""Build a library of circuits aggregated from all the interfaces."""

from typing import List

from transpile_benchy.interfaces.mqt_interface import MQTBench
from transpile_benchy.interfaces.qasm_interface import (
    BQSKitInterface,
    QASMBench,
    RedQueen,
)
from transpile_benchy.interfaces.qiskit_interface import QiskitCircuitInterface


class Library:
    """A class to handle the library of circuits."""

    def __init__(self, circuit_list=List[str]):
        """Initialize the library."""
        self.interfaces = []
        self.interfaces.append(QASMBench())
        self.interfaces.append(RedQueen())
        self.interfaces.append(MQTBench(num_qubits=0))
        self.interfaces.append(BQSKitInterface())
        self.interfaces.append(QiskitCircuitInterface(num_qubits=0))
        self.circuit_list = circuit_list

    @classmethod
    def from_txt(cls, filename):
        """Initialize the library from a text file."""
        with open(filename, "r") as f:
            circuit_list = f.read().splitlines()
        return cls(circuit_list)

    def __iter__(self):
        """Return an iterator over QuantumCircuits."""
        self.index = 0
        return self

    def __next__(self):
        """Return the next QuantumCircuit."""
        if self.index < len(self.circuit_list):
            circuit = self.get_circuit(self.circuit_list[self.index])
            self.index += 1
            return circuit
        else:
            raise StopIteration

    def get_circuit(self, circuit_name):
        """Return a circuit from the library."""
        # Extract the base name and the number of qubits from the circuit name
        base_name, num_qubits = circuit_name.rsplit("_", 1)
        num_qubits = int(num_qubits)

        for interface in self.interfaces:
            # If the interface requires num_qubits,
            # set it before trying to load the circuit
            if isinstance(interface, QiskitCircuitInterface) or isinstance(
                interface, MQTBench
            ):
                interface.set_num_qubits(num_qubits)
                try:
                    return interface._load_circuit(base_name + "_0")
                except CircuitNotFoundError:
                    continue
            else:
                try:
                    return interface._load_circuit(circuit_name)
                except CircuitNotFoundError:
                    continue
        raise ValueError(f"Circuit '{circuit_name}' not found in any interface")


class CircuitNotFoundError(Exception):
    """Exception raised when a circuit is not found in the library."""

    pass
