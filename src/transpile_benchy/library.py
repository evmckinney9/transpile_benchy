"""Build a library of circuits aggregated from all the interfaces."""

from typing import List

from transpile_benchy.interfaces.abc_interface import SubmoduleInterface

# from transpile_benchy.interfaces.mqt_interface import MQTBench
from transpile_benchy.interfaces.qasm_interface import (
    BQSKitInterface,
    QASMBench,
    RedQueen,
    Hardcoded,
)
from transpile_benchy.interfaces.qiskit_interface import QiskitCircuitInterface


class CircuitLibrary:
    """A class to handle the library of circuits."""

    def __init__(
        self,
        circuit_list: List[str],
        interfaces: List[SubmoduleInterface] = None,
    ):
        """Initialize the library."""
        if interfaces:
            self.interfaces = interfaces
        else:  # add all interfaces
            self.interfaces = []
            # hardcoded goes first so it will skip loading from others
            self.interfaces.append(Hardcoded())
            self.interfaces.append(QASMBench())
            self.interfaces.append(RedQueen())
            # self.interfaces.append(MQTBench(num_qubits=0))
            self.interfaces.append(BQSKitInterface())
            self.interfaces.append(QiskitCircuitInterface(num_qubits=0))

        self.circuit_list = circuit_list
        # TODO enforce naming convention here instead of later

        # verify that all circuits are in the library
        for circuit_name in self.circuit_list:
            if not any(
                circuit_name in interface for interface in self.interfaces
            ):
                raise ValueError(
                    f"Circuit '{circuit_name}' not found in any interface"
                )

    def circuit_count(self) -> int:
        """Return the number of circuits in the library."""
        return len(self.circuit_list)

    @classmethod
    def from_txt(cls, filename):
        """Initialize the library from a text file."""
        with open(filename, "r") as f:
            circuit_list = f.read().splitlines()
        return cls(circuit_list)

    @classmethod
    def from_submodules(cls, submodules):
        """Initialize the library from a list of submodules."""
        circuit_list = []
        for submodule in submodules:
            circuit_list.extend(submodule._get_all_circuits())
        return cls(circuit_list, submodules)

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
        # some conventions use name_n{num_qubits}, others use name_{num_qubits}
        base_name, num_qubits = circuit_name.rsplit("_", 1)
        if num_qubits.startswith("n"):
            num_qubits = num_qubits[1:]
        circuit_name = (
            f"{base_name}_n{num_qubits}"  # enforce qasm name convention
        )
        num_qubits = int(num_qubits)

        for interface in self.interfaces:
            if circuit_name in interface:
                if interface.dynamic:
                    print(
                        f"Loading {circuit_name} from {interface.__class__.__name__}"
                    )
                    return interface._load_circuit(base_name, num_qubits)
                else:
                    print(
                        f"Loading {circuit_name} from {interface.__class__.__name__}"
                    )
                    return interface._load_circuit(circuit_name)
            else:
                pass  # don't use continue, since this is subroutine of generator
        raise ValueError(
            f"Circuit '{circuit_name}' not found in any interface"
        )
