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
from typing import Iterator, List, Optional

from mqt.bench.benchmark_generator import get_benchmark
from mqt.bench.utils import get_supported_benchmarks

# from qiskit.circuit.exceptions import QasmError
from qiskit import QuantumCircuit


class SubmoduleInterface(ABC):
    """Abstract class for a submodule."""

    def __init__(self) -> None:
        """Initialize submodule."""
        self.raw_circuits = None

    def get_quantum_circuits(self) -> Iterator[QuantumCircuit]:
        """Return an iterator over filtered QuantumCircuits."""
        for qc in self._get_quantum_circuits():
            yield qc

    @abstractmethod
    def _get_quantum_circuits(self) -> Iterator[QuantumCircuit]:
        """Return an iterator over QuantumCircuits."""
        raise NotImplementedError

    def circuit_count(self) -> int:
        """Return total number of QuantumCircuits post filtering."""
        return len(self.raw_circuits)


class MQTBench(SubmoduleInterface):  # TODO needs filtering
    """Submodule for MQTBench circuits."""

    def __init__(
        self, num_qubits: int, filter_list: Optional[List[str]] = None
    ) -> None:
        """Initialize MQTBench submodule."""
        super().__init__()
        self.num_qubits = num_qubits
        self.raw_circuits = get_supported_benchmarks()
        self.raw_circuits = self.get_filtered_files(filter_list)

    def __str__(self):
        """Build string as all the available circuit names."""
        return str([s for s in self.raw_circuits])

    def get_filtered_files(self, filter_list) -> List:
        """Return a list of filtered QASM files."""
        if filter_list is None or self.raw_circuits is None:
            return self.raw_circuits

        return [
            s
            for s in self.raw_circuits
            if any(re.search(pattern, s) for pattern in filter_list)
        ]

    def _get_quantum_circuits(self) -> Iterator[QuantumCircuit]:
        """Return an iterator over QuantumCircuits."""
        for bench_str in self.raw_circuits:
            if bench_str in ["shor", "groundstate"]:
                continue  # NOTE way too big
                # yield get_benchmark(
                #     benchmark_name=bench_str,
                #     level="alg",
                #     circuit_size=self.num_qubits,
                #     benchmark_instance_name="xsmall"
                # )
            else:
                yield get_benchmark(
                    benchmark_name=bench_str,
                    level="alg",
                    circuit_size=self.num_qubits,
                )
