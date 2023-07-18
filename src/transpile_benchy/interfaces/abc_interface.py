"""This is the interface for quantum circuit sources, i.e., submodules.

The base class SubmoduleInterface has the abstract method
get_quantum_circuits(), which should return a list of QuantumCircuits.
This class is intended to be subclassed for different sources of
QuantumCircuits. Example subclasses provided are QASMBench and RedQueen.

File is written with intention that a submodule could either be written
in the form of having a list of QASM files, or having a set of functions
which return QuantumCircuits. The latter is not yet implemented.

Also, we write using Iterator, for sake of memory efficiency, don't want
to spend time building all QuantumCircuits, only build them when needed.
"""
import re
from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Dict, List, Optional

# from qiskit.circuit.exceptions import QasmError
from qiskit import QuantumCircuit

from transpile_benchy.library import CircuitNotFoundError


class SubmoduleInterface(Iterator[QuantumCircuit], ABC):
    """Abstract class for a submodule."""

    def __init__(self, filter_config: Optional[Dict[str, List[str]]]) -> None:
        """Initialize submodule."""
        self.filter_config = filter_config
        all_circuits = self._get_all_circuits()
        self.circuits = self._filter(all_circuits)
        self.circuit_iter = iter(self.circuits)

    def __iter__(self) -> Iterator[QuantumCircuit]:
        """Return an iterator over QuantumCircuits."""
        return self

    def __next__(self) -> QuantumCircuit:
        """Return the next QuantumCircuit."""
        return self._load_circuit(next(self.circuit_iter))

    @abstractmethod
    def _get_all_circuits(self) -> List[str]:
        """Return a list of all possible circuits."""
        raise NotImplementedError

    def _filter(self, circuits: List) -> List:
        """Filter the list of circuits based on the filter_config."""
        if self.filter_config is None:
            return circuits

        include = self.filter_config.get("include", None)
        exclude = self.filter_config.get("exclude", None)

        if include is not None:
            circuits = filter(
                lambda circuit: any(
                    re.search(pattern, str(circuit)) for pattern in include
                ),
                circuits,
            )

        if exclude is not None:
            circuits = filter(
                lambda circuit: all(
                    re.search(pattern, str(circuit)) is None for pattern in exclude
                ),
                circuits,
            )

        return list(circuits)

    @abstractmethod
    def _load_circuit(self, circuit_ir) -> QuantumCircuit:
        """Load a QuantumCircuit from a string."""
        raise CircuitNotFoundError

    def circuit_count(self) -> int:
        """Return total number of QuantumCircuits post-filtering."""
        return len(self.circuits)

    def __len__(self) -> int:
        """Return total number of QuantumCircuits post-filtering."""
        return self.circuit_count()
