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

from transpile_benchy.interfaces.errors import CircuitNotFoundError


class SubmoduleInterface(Iterator[QuantumCircuit], ABC):
    """Abstract submodule, which is an iterable over QuantumCircuits.

    This class represents an interface to a collection of QuantumCircuits.
    It can be iterated over to yield individual circuits, and has a filtering mechanism
    for selecting a subset of circuits based on user-specified criteria.

    Attributes:
        filter_config: A dictionary specifying inclusion and/or exclusion filters.
        circuits: List of all circuits after applying the filtering criteria.
        circuit_iter: An iterator over the filtered circuits.
        dynamic: A boolean indicating whether the submodule is dynamic, i.e., whether
                    the circuits can be generated with variable number of qubits.
    """

    def __init__(
        self, filter_config: Optional[Dict[str, List[str]]], dynamic=False
    ) -> None:
        """Initialize the submodule with optional filtering criteria.

        Creates an iterator over QuantumCircuits that match the filter criteria.

        Args:
            filter_config: A dictionary specifying inclusion and/or exclusion filters.
                           Each filter is a list of regex patterns. Circuits matching
                           any pattern in the 'include' filter and not matching any
                           pattern in the 'exclude' filter are included.
                           If filter_config is None, all circuits are included.
        """
        self.filter_config = filter_config
        all_circuits = self._get_all_circuits()
        self.circuits = self._filter(all_circuits)
        self.circuit_iter = iter(self.circuits)
        self.dynamic = dynamic

    def __contains__(self, circuit_name: str) -> bool:
        """Return True if the specified circuit is in the iteration."""
        # if dynamic, remove the number of qubits from the circuit name
        # (assume it's at the end)
        if self.dynamic:
            circuit_name = circuit_name.rsplit("_", 1)[0]
        return circuit_name in self.circuits

    def __iter__(self) -> Iterator[QuantumCircuit]:
        """Return an iterator over QuantumCircuits."""
        return self

    def __next__(self) -> QuantumCircuit:
        """Return the next QuantumCircuit in the iteration."""
        return self._load_circuit(next(self.circuit_iter))

    def circuit_count(self) -> int:
        """Return total number of QuantumCircuits in the iteration."""
        return len(self.circuits)

    def __len__(self) -> int:
        """Return total number of QuantumCircuits in the iteration."""
        return self.circuit_count()

    @abstractmethod
    def _get_all_circuits(self) -> List[QuantumCircuit]:
        """All possible QuantumCircuits.

        Return a list of all possible QuantumCircuit instances that this
        submodule can generate.

        This method needs to be implemented by any concrete subclass.

        Returns:
            A list of all QuantumCircuit instances.
        """
        raise NotImplementedError

    @abstractmethod
    def _load_circuit(self, circuit_name: str) -> QuantumCircuit:
        """Load a QuantumCircuit from its name.

        This method needs to be implemented by any concrete subclass.

        Args:
            circuit_name: The string representation of the QuantumCircuit.

        Returns:
            A QuantumCircuit instance.

        Raises:
            CircuitNotFoundError: If the specified circuit cannot be loaded.
        """
        raise CircuitNotFoundError

    def _filter(self, circuits: List[str]) -> List[str]:
        """Filter the list of circuits based on the filter_config.

        Circuits matching any pattern in the 'include' filter and not matching
        any pattern in the 'exclude' filter are included.

        Args:
            circuits: The list of QuantumCircuit strings to filter.

        Returns:
            A new list of QuantumCircuit strings that match the filter criteria.
        """
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
