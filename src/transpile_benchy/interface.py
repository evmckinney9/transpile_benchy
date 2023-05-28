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
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterator, List

# from qiskit.circuit.exceptions import QasmError
from qiskit import QuantumCircuit


class SubmoduleInterface(ABC):
    """Abstract class for a submodule."""

    @abstractmethod
    def get_quantum_circuits(self) -> Iterator[QuantumCircuit]:
        """Return an iterator over QuantumCircuits."""
        pass

    @abstractmethod
    def estimate_circuit_count(self) -> int:
        """Return an estimate of the total number of QuantumCircuits.

        Note that this assumes that generating the quantum circuits
        doesn't significantly change the total number of circuits, which
        might not be the case if some files fail to load or are filtered
        out.
        """
        pass


class QASMInterface(SubmoduleInterface):
    """Abstract class for a submodule that has QASM files."""

    def _load_qasm_file(self, file: Path) -> QuantumCircuit:
        """Load a QASM file."""
        try:
            with open(file, "r") as f:
                qc = QuantumCircuit.from_qasm_str(f.read())
                qc.name = file.stem
            return qc
        except Exception as e:
            print(f"Failed to load {file}: {e}")
            return None

    def get_quantum_circuits(self) -> Iterator[QuantumCircuit]:
        """Return an iterator over QuantumCircuits."""
        for file in self.qasm_files:
            yield self._load_qasm_file(file)

    def estimate_circuit_count(self) -> int:
        """Return an estimate of the total number of QuantumCircuits."""
        return len(self.qasm_files)

    @abstractmethod
    def _get_qasm_files(self, directory: str) -> List[Path]:
        """Return a list of QASM files."""
        raise NotImplementedError


class QASMBench(QASMInterface):
    """Submodule for QASMBench circuits."""

    def __init__(self, size: str):
        """Initialize QASMBench submodule.

        size: 'small', 'medium', or 'large'
        """
        self.size = size
        self.qasm_files = self._get_qasm_files("QASMBench", self.size)

    @staticmethod
    def _get_qasm_files(directory: str, size: str) -> List[Path]:
        """Return a list of QASM files."""
        prepath = Path(__file__).resolve().parent.parent.parent
        qasm_files = prepath.glob(f"submodules/{directory}/{size}/**/*.qasm")
        # filter out the transpiled files
        qasm_files = filter(lambda file: "_transpiled" not in str(file), qasm_files)
        # harcode, remove these files that are just way too big
        too_big = ["vqe", "bwt"]
        qasm_files = filter(
            lambda file: not any(x in str(file) for x in too_big), qasm_files
        )
        return list(qasm_files)


class RedQueen(QASMInterface):
    """Submodule for RedQueen circuits."""

    def __init__(self):
        """Initialize RedQueen submodule."""
        self.qasm_files = self._get_qasm_files("red-queen", self.size)

    @staticmethod
    def _get_qasm_files(directory: str) -> List[Path]:
        """Return a list of QASM files."""
        prepath = Path(__file__).resolve().parent.parent.parent
        qasm_files = prepath.glob(
            f"submodules/{directory}/red_queen/games/applications/qasm/*.qasm"
        )
        return list(qasm_files)
